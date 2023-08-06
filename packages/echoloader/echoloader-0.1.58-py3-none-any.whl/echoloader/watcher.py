import argparse
import base64
import csv
import datetime
import hashlib
import io
import itertools
import json
import logging
import math
import os
import re
import socket
import sys
import threading
import time
import traceback
from getpass import getpass
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from multiprocessing import Pool
from time import sleep

import cv2
import imageio
import numpy as np
import pydicom
import requests
from pathy import Pathy
from pydicom import uid
from pydicom._uid_dict import UID_dictionary
from pydicom.encaps import decode_data_sequence
from pydicom.encaps import encapsulate, generate_pixel_data_frame
from pydicom.errors import InvalidDicomError
from pydicom.filewriter import write_file_meta_info
from pydicom.pixel_data_handlers import apply_color_lut
from pynetdicom import AE, evt, ALL_TRANSFER_SYNTAXES, sop_class
from tqdm import tqdm
from watchdog.events import FileCreatedEvent, FileMovedEvent, FileModifiedEvent
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

from echoloader.lib import unpack
from echoloader.sync import PacsConnection, Sync, DEFAULT_AE_TITLE, server_context

logger = logging.getLogger('echolog')
OS_VAR_PREFIX = 'US2_'
for k in ['1.2.840.10008.5.1.4.1.1.3', '1.2.840.10008.5.1.4.1.1.6']:
    sop_class._STORAGE_CLASSES[UID_dictionary[k][-1]] = k


def setup_logging(filename=None, verbose=None):
    if verbose:
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
    if filename:
        fh = logging.FileHandler(filename)
        logging.getLogger().addHandler(fh)


class ENV:
    def __init__(self, env):
        prefix = f'{env}-'.replace('production-', '')
        self.cloud = '://' not in env
        self.api_url = f"https://{prefix}api.us2.ai" if self.cloud else env


def call_repeatedly_fail_safe(interval, func, *args, timeout=5):
    stopped = threading.Event()

    def loop():
        while not stopped.wait(interval):  # the first call is in `interval` secs
            logger.error('Hello there')
            while True:
                try:
                    func(*args)
                    break
                except Exception as exc:
                    logger.error(f'Failed to call {func.__name__} due to {exc}, retrying in {timeout}s')
                    sleep(timeout)

    t = threading.Thread(target=loop)
    t.daemon = True
    t.start()
    return stopped.set


class Auth:
    def __init__(self, args, username, password):
        self.args = args
        self.api_url = args.env.api_url
        self.username = username
        self.password = password
        self.id_token = ''
        self.refresh_token = ''
        self.payload = {}
        self.exp = 0
        self.groups = []
        self.sub = ''
        self.authenticate()
        time_till_exp = self.exp - time.time()
        call_repeatedly_fail_safe(time_till_exp * 3 / 4, self.refresh)

    def expired(self):
        return time.time() > self.exp

    def unpack_auth(self, request):
        data = unpack(request)
        auth = data['AuthenticationResult']
        self.id_token = auth['IdToken']
        self.refresh_token = auth.get('RefreshToken', self.refresh_token)
        self.payload = json.loads(base64.b64decode(self.id_token.split('.')[1] + '===').decode())
        self.exp = self.payload['exp']
        user = unpack(requests.get(f"{self.api_url}/users/current", headers=self.get_headers()))
        self.groups = user.get('permissions', [])
        self.sub = user.get('cognito_id')

    def authenticate(self):
        self.unpack_auth(
            requests.post(f"{self.api_url}/users/login", json={'username': self.username, 'password': self.password}),
        )

    def refresh(self):
        try:
            self.unpack_auth(
                requests.post(f"{self.api_url}/users/refresh", json={'refreshToken': self.refresh_token}),
            )
        except Exception as exc:
            logger.warning(f'Failed to renew token due to {exc}, re-authenticating')
            self.authenticate()

    def customer(self):
        groups = self.groups
        s3 = [g for g in groups if g.startswith('s3-')]
        if s3:
            return s3[0].split('-', 1)[1]
        if 'upload' in groups:
            return self.sub

    def get_headers(self):
        return {"Authorization": f"Bearer {self.id_token}"}


def is_video(img=None, shape=None):
    shape = shape or (isinstance(img, np.ndarray) and img.shape)
    return shape and (len(shape) == 4 or (len(shape) == 3 and shape[-1] > 4))


def ybr_to_rgb(img):
    return cv2.cvtColor(img, cv2.COLOR_YCR_CB2BGR)


def blank_top_bar(media, regions):
    video = is_video(media)
    image = np.mean(media, axis=0) if video else media
    new_image = np.mean(image[..., :3], axis=-1) if 3 <= image.shape[-1] <= 4 else image
    binary_image = (new_image > 2).astype('uint8')
    h = int(binary_image.shape[0] * 0.2)
    sum_pixel = np.sum(binary_image[:h, :], axis=1)
    top_bar = np.where(sum_pixel > (binary_image.shape[0] * 0.88))
    top_bar_bottom = 0
    if len(top_bar[0]) != 0:
        new_image[top_bar, :] = 0
        image[top_bar, :] = 0
        top_bar_bottom = top_bar[0][-1] + 1
    top_bar_bottom = max(top_bar_bottom, 40)
    mask = np.ones_like(media[0] if video else media)
    mask[:top_bar_bottom] = 0
    for region in regions:
        xo, xn = region.RegionLocationMinX0, region.RegionLocationMaxX1
        yo, yn = region.RegionLocationMinY0, region.RegionLocationMaxY1
        mask[yo:yn, xo:xn] = 1
    media *= mask
    return media


def mpeg4hp41(ds):
    frames = imageio.mimread(next(generate_pixel_data_frame(ds.PixelData)), memtest=False, format='mp4')
    return np.asarray(frames)


def unusual_frame_mean(px: np.ndarray, threshold=100):
    """
    If mean pixel value of frame is larger than threshold, background is likely non-black
    (usually happens when dicom tag is RGB but the frames are actually in YBR).
    """
    frame = px[px.shape[0] // 2] if is_video(px) else px  # take middle frame for video
    return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)[..., -1].mean() > threshold


def media_iter(dicom):
    try:
        seq = decode_data_sequence(dicom.PixelData)
        if not seq:
            raise ValueError('No data sequence found')
        for b in seq:
            yield imageio.imread(io.BytesIO(b))
    except Exception as exc:
        logger.info(f'Failed to decode JPEG compressed frame bytes due to {exc}, falling back to pixel_array')
        handler = parse_dicom_pixel.custom_handlers.get(dicom.file_meta.TransferSyntaxUID)
        px = handler(dicom) if handler else dicom.pixel_array
        if isinstance(px, np.ndarray) and not is_video(px):
            px = [px]
        yield from px


def parse_dicom_pixel(dicom, anonymize=True):
    """Parse color space and coerce to RGB, and anonymize by blanking out top bar."""
    px = media_iter(dicom)
    pi = dicom.PhotometricInterpretation
    px = (ybr_to_rgb(img) if pi in ['YBR_FULL', 'YBR_FULL_422', 'RGB'] and unusual_frame_mean(img) else img
          for img in px)
    px = ((apply_color_lut(img, dicom) // 255).astype('uint8') if pi in ['PALETTE COLOR'] else img for img in px)
    px = (np.repeat(np.expand_dims(img, -1), 3, -1) if len(img.shape) < 3 else img for img in px)
    if anonymize:
        px = (blank_top_bar(img, getattr(dicom, "SequenceOfUltrasoundRegions", [])) for img in px)
    sample = next(px)
    px = itertools.chain([sample], px)
    shape = (getattr(dicom, 'NumberOfFrames', 1), *sample.shape)
    return px, shape


parse_dicom_pixel.custom_handlers = {
    uid.MPEG4HP41: mpeg4hp41,
}


def ensure_even(stream):
    # Very important for some viewers
    if len(stream) % 2:
        return stream + b"\x00"
    return stream


def person_data_callback(ds, e):
    if e.VR == "PN" or e.tag == (0x0010, 0x0030):
        del ds[e.tag]


def pad_to_multiple(arr, size, dims=(1, 2)):
    pad_dims = [(0, size - (s % size)) if i in dims else (0, 0) for i, s in enumerate(arr.shape)]
    return np.pad(arr, pad_dims, 'constant')


def package_dicom(ds, anonymize, compress):
    # Populate required values for file meta information
    ds.remove_private_tags()
    if not anonymize and not compress:
        return
    media, shape = parse_dicom_pixel(ds, anonymize)
    if anonymize:
        ds.walk(person_data_callback)
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    ds.BitsStored = 8
    ds.BitsAllocated = 8
    ds.HighBit = 7
    ds.Rows, ds.Columns, ds.SamplesPerPixel = shape[1:]
    ds.PhotometricInterpretation = "YBR_FULL_422"
    if shape[0] > 1:
        ds.StartTrim = 1
        ds.StopTrim = ds.NumberOfFrames = shape[0]
        fps = getattr(ds, 'CineRate', 1000 / getattr(ds, 'FrameTime', 40))
        ds.CineRate = ds.RecommendedDisplayFrameRate = round(fps, 2)
        ds.FrameTime = 1000 / ds.CineRate
        ds.ActualFrameDuration = math.ceil(1000 / ds.CineRate)
        ds.PreferredPlaybackSequencing = 0
        ds.FrameDelay = 0
        if compress:
            ds.file_meta.TransferSyntaxUID = uid.MPEG4HP41
            ds.PixelData = encapsulate([
                imageio.mimwrite(imageio.RETURN_BYTES, (pad_to_multiple(img, 16, (0, 1)) for img in media), fps=fps,
                                 format='mp4')])
        else:
            ds.file_meta.TransferSyntaxUID = uid.JPEGBaseline8Bit
            ds.PixelData = encapsulate([imageio.imwrite(imageio.RETURN_BYTES, img, format='jpg') for img in media])
    else:
        ds.file_meta.TransferSyntaxUID = uid.JPEGBaseline8Bit
        ds.PixelData = encapsulate([imageio.imwrite(imageio.RETURN_BYTES, next(media), format='jpg')])
    ds['PixelData'].is_undefined_length = True


def size(path):
    stat = path.stat()
    return getattr(stat, 'size', getattr(stat, 'st_size', None))


def wait_file(path):
    path = Pathy.fluid(path)
    old = None
    cur = size(path)
    while old != cur or not cur:
        sleep(1)
        old, cur = cur, size(path)


def create_proxy(args):
    class Proxy(SimpleHTTPRequestHandler):
        def do_request(self, method):
            url = f'{args.auth.api_url}{self.path}'
            headers = dict(self.headers)
            headers.update(args.auth.get_headers())
            headers['Host'] = 'proxy.us2.ai'
            data = self.rfile.read(int(self.headers['Content-Length'] or 0))
            response = getattr(requests, method)(url, headers=headers, stream=True, data=data)
            self.send_response(response.status_code)
            for k, v in response.headers.items():
                self.send_header(k, v)
            self.end_headers()
            self.copyfile(response.raw, self.wfile)

        def do_GET(self):
            self.do_request('get')

        def do_PUT(self):
            self.do_request('put')

        def do_POST(self):
            self.do_request('post')

        def do_DELETE(self):
            self.do_request('delete')

        def do_OPTIONS(self):
            self.do_request('options')

    return Proxy


def initializer(filename, verbose):
    setup_logging(filename, verbose)


class Handler(FileSystemEventHandler):
    def __init__(self, args):
        self.args = args
        self.pool = Pool(args.n, initializer=initializer, initargs=(args.log, args.verbose))
        self.pbar = tqdm(total=0)
        if self.args.csv_out:
            csv.writer(open(self.args.csv_out, 'a', newline='')).writerow(
                ['customer', 'trial', 'patientID', 'visit', 'filename'])

    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['pool']
        del self_dict['pbar']
        return self_dict

    def __setstate__(self, state):
        self.__dict__.update(state)

    def processing(self):
        return self.pbar.n < self.pbar.total

    def stop(self):
        self.pool.terminate()

    def join(self):
        self.pool.join()

    def handle_err(self, err, vargs, kwargs):
        if isinstance(err, InvalidDicomError):
            logger.debug(f'Error during process call: {err}, vargs: {vargs}, kwargs: {kwargs}')
            self.pbar.total -= 1
            self.pbar.update(0)
            return
        logger.error(f'Error during process call: {err}, vargs: {vargs}, kwargs: {kwargs}')
        logger.debug(traceback.format_tb(err.__traceback__))
        self.pbar.update(1)

    def handle(self, *vargs, **kwargs):
        self.pbar.total += 1
        self.pbar.refresh()
        self.pbar.disable = False
        worker = HandlerWorker(self, *vargs, **kwargs)
        self.pool.apply_async(worker.process,
                              error_callback=lambda err: self.handle_err(err, vargs, kwargs),
                              callback=lambda _: self.pbar.update(1))

    def on_any_event(self, event):
        logger.debug(f'got event {event}')
        if isinstance(event, (FileCreatedEvent, FileMovedEvent, FileModifiedEvent)):
            path = event.src_path
            wait_file(path)
            self.handle(path)


class HandlerWorker:
    def __init__(self, handler: Handler, path=None, ds=None, ae_title=None, f=None, **kwargs):
        self.path = path
        self.kwargs = kwargs
        self.ds = ds
        self.ae_title = ae_title
        self.f = f
        self.args = handler.args

    def file_params(self, ds, ae_title, filename=None):
        customer = getattr(self.args, 'customer', '') or ae_title
        stem = '_'.join(map(str, filter(bool, [ds.SOPInstanceUID, filename])))
        kwargs = self.kwargs
        return {
            'customer': customer or '',
            'trial': kwargs.get('trial') or getattr(self.args, 'trial', None) or customer or '',
            'patient_id': kwargs.get('patient_id') or ds.PatientID,
            'visit_id': kwargs.get('visit_id') or ds.StudyID or ds.StudyInstanceUID or ds.StudyDate or 'No Study ID',
            'filename': kwargs.get('filename') or f"{stem}.dcm",
        }

    def upload(self, ds, param):
        logger.info(f'uploading {param}')
        content_type = 'application/dicom'
        auth = self.args.auth
        env = self.args.env
        headers = auth.get_headers()
        param['content_type'] = content_type
        upload_param = {}
        url = f"{auth.api_url}/dicom/upload"
        if env.cloud:
            r = requests.get(url, params=param, headers=headers)
            d = unpack(r)
            url = d['url']
            headers = d['headers']
        else:
            upload_param = param
        buf = BytesIO()
        ds.save_as(buf)
        buf.seek(0)
        return unpack(requests.put(url, data=buf.read(), headers=headers, params=upload_param))

    def pseudonymize(self, ds):
        for tag in self.args.pseudonymize:
            old = getattr(ds, tag)
            new = hashlib.sha256(old.encode()).hexdigest()[:8]
            logger.info(f'Pseudonymizing {tag} from {getattr(ds, tag)} to {new}')
            if self.args.pseudonymize_file:
                f = Pathy.fluid(self.args.pseudonymize_file).open('w+')
                k = f"{tag},{old},{new}"
                if k not in set(f):
                    f.write(f"{k}\n")
            setattr(ds, tag, new)

    def process(self):
        try:
            path = self.path and Pathy.fluid(self.path)
            ds = self.ds or pydicom.dcmread(self.f or path.open('rb'), force=True)
            params = self.file_params(ds, ae_title=self.ae_title, filename=getattr(path, 'stem', None))
            logger.info(f'processing {params}')
            extracted = self.args.extracted
            k = tuple(params.values())
            if k not in extracted:
                if self.args.filter and not all(eval(f, {'ds': ds}) for f in self.args.filter):
                    logger.info(f'Skipping {ds.SOPInstanceUID} due to no matching filter')
                    return
                package_dicom(ds, anonymize=self.args.anonymize, compress=self.args.compress)
                if self.args.pseudonymize:
                    self.pseudonymize(ds)
                dst = self.args.dst
                if dst:
                    src = self.args.src
                    rel = path.relative_to(src) if src else f"{ds.SOPInstanceUID}.dcm"
                    out = (Pathy.fluid(dst) / rel).with_suffix(".dcm")
                    if self.args.overwrite or not out.is_file():
                        out.parent.mkdir(exist_ok=True, parents=True)
                        ds.save_as(out.open('wb'))
                if hasattr(self.args, "auth"):
                    self.upload(ds, params)
                extracted.add(k)
                if self.args.csv_out:
                    csv.writer(open(self.args.csv_out, 'a', newline='')).writerow(k)
        except Exception as exc:
            if self.args.save_failed and self.f:
                try:
                    self.f.seek(0)
                    self.args.save_failed.mkdir(parents=True, exist_ok=True)
                    dst = Pathy.fluid(self.args.save_failed) / f'{datetime.datetime.now().strftime("%m%d%Y%H%M%S")}.dcm'
                    dst.open('wb').write(self.f.read())
                except Exception as e:
                    logger.error(f'Error saving failed: {e}')
                    logger.debug(traceback.format_tb(e.__traceback__))
            raise exc
        finally:
            if self.f:
                self.f.close()


def handle_store(event, handler):
    """Handle EVT_C_STORE events."""
    f = io.BytesIO()
    f.write(b'\x00' * 128)
    f.write(b'DICM')
    # Encode and write the File Meta Information
    write_file_meta_info(f, event.file_meta)
    # Write the encoded dataset
    f.write(event.request.DataSet.getvalue())
    f.seek(0)
    handler.handle(f=f, ae_title=event.assoc.remote['ae_title'].strip().decode())
    return 0x0000


def extracted_list(path):
    path = path and Pathy.fluid(path)
    if path and path.is_file():
        return {tuple(row) for row in csv.reader(path.open())}


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'
    finally:
        s.close()


def read_args():
    parser = argparse.ArgumentParser('EchoLoader')
    parser.add_argument(
        "--src",
        help="The folder to anonymize")
    parser.add_argument(
        "--src-details",
        help="Regular expression to apply on path to extract patient details used in the upload request. "
             "Can use (?P<key>re) to capture regular expression re to key. "
             "Key can be trial, patient_id, visit_id or filename")
    parser.add_argument(
        "--dst",
        help="The output folder for the anonymized DICOM, defaults to src folder suffixed with '_anonymized'")
    parser.add_argument(
        "--watch", action="store_true",
        help="Watch the src folder for changes")
    parser.add_argument(
        "--pacs", action="store_true",
        help="Starts PACS server")
    parser.add_argument(
        "--secure", nargs=3,
        help="Enable Secure PACS, must include 3 arguments which are paths to: "
             "CA certificate, server certificate and server key")
    parser.add_argument(
        "--pacs-ae-title", default=DEFAULT_AE_TITLE,
        help="PACS AE Title, defaults to Us2.ai")
    parser.add_argument(
        "--pacs-port", default=11112, type=int,
        help="PACS port, defaults to 11112")
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite files in the output folder")
    parser.add_argument(
        "--n", type=int, default=4,
        help="Number of workers")
    parser.add_argument(
        "--upload", action='store_true',
        help="Will upload all anonymized imaging to Us2.ai cloud")
    parser.add_argument(
        "--env",
        help="The Us2.ai environment to use")
    parser.add_argument(
        "--extracted",
        help="File of cases to ignore - csv file with customer, trial, patientID, visit, filename")
    parser.add_argument(
        "--csv-out",
        help="Path to csv file of extracted cases")
    parser.add_argument(
        "--verbose", action='store_true',
        help="Enable all application debug/info logs")
    parser.add_argument(
        "--save-failed", type=Pathy.fluid,
        help="Path to store failed cases locally")
    parser.add_argument(
        '--no-anonymization', action='store_false', dest='anonymize',
        help="No anonymization of data prior to upload",
    )
    parser.add_argument(
        '--pseudonymize', nargs='+',
        help="DCM tags to pseudonymize",
    )
    parser.add_argument(
        '--pseudonymize-file',
        help="Path to file that will be output with mapping of original to pseudonymized values",
    )
    parser.add_argument(
        '--no-compression', action='store_false', dest='compress',
        help="Don't compress videos into mp4 format",
    )
    parser.add_argument(
        '--customer',
        help="The customer tag used for the upload (Admin only)",
    )
    parser.add_argument(
        '--sync',
        nargs='+',
        default=[],
        help="Will try to sync structured report back to specified location."
             "Format: IP:PORT:REMOTE_AE_TITLE[:LOCAL_AE_TITLE:CERT:KEY]",
    )
    parser.add_argument(
        '--sync-url',
        default=False,
        action='store_true',
        help='Include url to measurement page in SR export',
    )
    parser.add_argument(
        '--sync-main-findings',
        default=False,
        action='store_true',
        help='Include main findings in SR export/DICOM encapsulated PDF',
    )
    parser.add_argument(
        '--sync-pdf-images',
        default=False,
        action='store_true',
        help='Include images in DICOM encapsulated PDF',
    )
    parser.add_argument(
        '--sync-designators',
        nargs='+',
        help='Designators used for SR export',
    )
    parser.add_argument(
        '--sync-modalities',
        default=['SR'],
        nargs='+',
        help='Modalities that should be synced to PACS, valid values are SR, PS, SC',
    )
    parser.add_argument(
        '--sync-poll',
        default=2,
        type=float,
        help='Delay between polls',
    )
    parser.add_argument(
        '--sync-by-measurement',
        default=False,
        action='store_true',
        help='Will cause all PS/SC files to contain just one measurement each, instead of all for the frame',
    )
    parser.add_argument(
        '--sync-search',
        default=['reportCompleted=true'],
        help='Parameters for sync search, can be used to sync only when special criteria is met',
    )
    parser.add_argument(
        '--username',
        help='App username',
    )
    parser.add_argument(
        '--password',
        help='App password',
    )
    parser.add_argument(
        '--config-file',
        default=Pathy.fluid("config.json"),
        type=Pathy.fluid,
        help='Configuration file for the EchoLoader',
    )
    parser.add_argument(
        '--trial',
        help='Trial name of studies to upload',
    )
    parser.add_argument(
        '--proxy',
        help='Spin up a proxy against env on the given port',
        type=int,
    )
    parser.add_argument(
        '--log',
        help='File for logs',
    )
    parser.add_argument(
        '--filter',
        help='Inclusive filter for DS files to process',
        default=[],
        nargs='+',
    )
    parser.add_argument(
        '--src-glob',
        help='glob expression to apply on src directory',
        default='*',
    )
    args = parser.parse_args(sys.argv[1:])
    if args.config_file.is_file():
        with args.config_file.open() as f:
            for k, v in json.load(f).items():
                setattr(args, k, v)
    args.env = (args.env and ENV(args.env)) or ENV('production')
    args.src = args.src and Pathy.fluid(args.src)
    args.extracted = (args.extracted and extracted_list(args.extracted)) or set()
    args.sync = [PacsConnection(c) for c in args.sync]
    setup_logging(args.log, args.verbose)
    if args.upload or args.sync or args.proxy:
        args.auth = Auth(
            args,
            args.username or os.environ.get(f"{OS_VAR_PREFIX}COGNITO_USERNAME") or input("username: "),
            args.password or os.environ.get(f"{OS_VAR_PREFIX}COGNITO_PASSWORD") or getpass("password: "),
        )
        args.customer = args.customer or args.auth.customer()
    return args


def main():
    args = read_args()
    handler = Handler(args)
    sync = observer = pacs = httpd = None
    try:
        if args.src:
            src = args.src
            paths = [src] if src.is_file() else [p for p in src.rglob(args.src_glob) if p.is_file()]
            args.n = len(paths)
            args.i = 0
            details = args.src_details and re.compile(args.src_details)
            for i, path in enumerate(paths):
                kwargs = {}
                if details:
                    match = details.search(path.as_posix())
                    if match:
                        kwargs = match.groupdict()
                        s = f"Matched path details: {kwargs} on {path.as_posix()}"
                        logger.info(s)
                    else:
                        s = f"No match for path details regex on {path.as_posix()}"
                        logger.warning(s)
                    if i == 0 and input(f'{s}, Continue (y/n): ') != 'y':
                        return
                handler.handle(path, **kwargs)
            if args.watch:
                logger.warning(f"watching folder {os.path.abspath(src)}")
                src.mkdir(exist_ok=True, parents=True)
                observer = PollingObserver()
                observer.schedule(handler, src, recursive=True)
                observer.start()
        if args.sync:
            sync = Sync(args, handler.pool)
            sync.start()
        if args.pacs:
            logger.warning(
                f"Starting pacs server on {get_ip()}:{args.pacs_port} with AE title {args.pacs_ae_title}")
            handlers = [(evt.EVT_C_STORE, handle_store, [handler])]
            ae = AE(args.pacs_ae_title)
            for sop in UID_dictionary.keys():
                ae.add_supported_context(sop, ALL_TRANSFER_SYNTAXES)
            ae.maximum_pdu_size = 0
            pacs = ae.start_server(
                ('0.0.0.0', args.pacs_port),
                block=False,
                ssl_context=server_context(*args.secure) if args.secure else None,
                evt_handlers=handlers)
        if args.proxy:
            httpd = ThreadingHTTPServer(server_address=('0.0.0.0', args.proxy), RequestHandlerClass=create_proxy(args))
            thread = threading.Thread(target=httpd.serve_forever)
            thread.start()
        while observer or handler.processing() or sync or pacs or httpd:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.warning("Interrupted, finishing up jobs")
    finally:
        to_wait = [handler, observer, sync]
        to_wait = [e for e in to_wait if e]
        for e in to_wait:
            e.stop()
        for server in [pacs, httpd]:
            if server:
                server.shutdown()
        for e in to_wait:
            e.join()
