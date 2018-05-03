import astropy.io.fits as fitsio
import astropy.stats as stats
import numpy
import concurrent.futures as cf
from skimage import measure
import scipy.ndimage as ndimage
from  argparse import ArgumentParser
import logging
import sys
import pkg_resources

__version__ = pkg_resources.require("cleanmask")[0].version

morph = ndimage.morphology


def get_imslice(ndim):
    imslice = []
    for i in xrange(ndim):
        if i<ndim-2:
            imslice.append(0)
        else:
            imslice.append(slice(None))
    return imslice


def work(i, boxes, size, overlap, npix, iters, sigma, im):
    slice_list = []
    for j in xrange(boxes):
        logging.info("Sigma cliping RMS box ({0},{1})".format(i,j))
        xi, yi = i*size-overlap, j*size-overlap
        xf, yf = i*size + size + overlap, j*size + size + overlap

        xi, xf = sorted([xi,xf])
        yi, yf = sorted([yi,yf])

        # Boundary conditions
        if xi <0: 
            xi = 0 
        if yi < 0:
            yi = 0 

        if xf > npix:
            xf = npix
        if yf > npix:
            yf = npix
    
        imslice = [slice(xi, xf), slice(yi, yf)]
        tmp = im[imslice]
        slice_list.append([i, imslice, stats.sigma_clip(tmp, sigma=sigma, iters=iters).mask])
    return slice_list



def main(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit(): argv[i] = ' ' + arg 

    parser = ArgumentParser(description="Create a binary mask")
    add = parser.add_argument

    add("-v","--version", action='version', version='{0:s} version {1:s}'.format(parser.prog, __version__))
    add('-i', '--image', 
        help='iFITS image from which to derive the binary mask')

    add('-o', '--output', type=str,
        help='Name of resulting FITS mask image')

    add('-s', '--sigma', type=int, default=5,
        help='The number of standard deviations to use for both the lower and upper clipping limit.')

    add('-it', '--iters', type=int, default=3,
        help='The number of iterations to perform sigma clipping, or 0 to clip until convergence is achieved.')

    add('-nb', '--boxes', type=int, default=11,
        help='Will devide image into this number of boxes, then perform sigma clipping in each of those boxes')

    add('-ol', '--overlap', type=float, default=0,
        help='Overlap region. As a fraction of -nb/--boxes')

    add('-mv', '--mask-value', type=float, default=0,
        help='Value to use for masked regions.')

    add('-d', '--dilate', action='store_true',
        help='Dilate mask. This is an attempt to include low surface brightness in an image.')

    add('-t', '--tolerance', type=float, default=0.05,
        help=' Tolerance for dilating the mask. Will stop dilating if percentage difference between dilations is smaller than this value.')

    add('-di', '--diter', type=int, default=20,
        help='Maximum number of binary mask iterations per island.')

    add('-nn', '--no-negatives', action='store_true',
        help='Do not Include negative pixels when creating binary mask')

    add('-pf', '--peak-fraction', type=float,
        help='Clip image based on this fraction of the peak pixel in the image. Will ingore --sigma')

    add('-ll', '--log-level', type=str, choices=['INFO', 'DEBUG','CRITICAL', 'WARNING'],
        default='INFO',
        help='Log level')

    args = parser.parse_args(argv)
    outname = args.output or args.image[:-5]+"-masked.fits" 
    
    logging.basicConfig(level=getattr(logging, args.log_level))

    hdu = fitsio.open(args.image)
    data = hdu[0].data
    hdr = hdu[0].header
    npix = hdr["NAXIS1"]
    
    im = data[get_imslice(hdr["naxis"])]

    if args.peak_fraction:
        peak = im.max()
        mask = (im > peak*args.peak_fraction).astype(numpy.float32)

        if args.mask_value != 0:
            if isinstance(mask_value, (str, unicode)):
                if str(mask_value).lower()=="nan":
                    mask_value = numpy.nan
            mask[mask==0] = mask_value
        
        hdu[0].data = mask[numpy.newaxis, numpy.newaxis, ...]
        
        hdu.writeto(outname, clobber=True)
        hdu.close()

        logging.info("Sucessfully created binary mask.")
        sys.exit(0)

    
    size = npix/args.boxes
    overlap = int(size*args.overlap/2)
    mask = numpy.zeros(im.shape, dtype=numpy.float32)
    
    ex = cf.ProcessPoolExecutor(8)
    futures = []
    
    for i in xrange(args.boxes):
        f = ex.submit(work, i, boxes=args.boxes, size=size, overlap=overlap, npix=npix, iters=args.iters, sigma=args.sigma, im=im)
        futures.append(f)
    
    logging.info("Creating mask...")
    for i, f in enumerate(cf.as_completed(futures)):
        for j, imslice, submask in f.result():
            mask[imslice] = submask
    
    if args.no_negatives:
        mask[im<0] = 0
    
    islands = measure.label(mask, background=0)
    labels = set(islands.flatten())
    labels.remove(0)
    
    centre = lambda island : map(int, [island[0].mean(), island[1].mean()])
    def extent(isl):
        nisl = len(isl[0])
        r = []
        for i in xrange(nisl):
            for j in xrange(i,nisl):
                a = isl[0][i], isl[1][i]
                b = isl[0][j], isl[1][j]
                rad = (a[0]-b[0])**2 + (a[1]-b[1])**2
                r.append(int(rad**0.5))
        return max(r)
    
    if args.dilate:
        logging.info("The mask has {0} islands. Will now attempt to dilate".format(len(labels)))
        for i,label in enumerate(labels):
            logging.info("Dilating island {0} of {1}".format(i+1, len(labels)))

            island = numpy.where(islands==label)
            rx, ry = centre(island)
            size = int(extent(island) * 1.5)
            xi, yi = rx - size, ry - size
            xf, yf = rx + size, ry + size
        
            if xi <0: 
                xi = 0 
            if yi < 0:
                yi = 0 
        
            if xf > npix:
                xf = npix
            if yf > npix:
                yf = npix
        
            imslice = [slice(xi, xf), slice(yi, yf)]
            imask = mask[imslice]
            iim = im[imslice]
        
            f0 = (iim*imask).sum()
            make_bigger = f0 > 0.0
            struct = ndimage.generate_binary_structure(2, 2)
            counter = 0
            nmask = morph.binary_dilation(imask, structure=struct, iterations=1).astype(imask.dtype)
    
            while make_bigger:
                f1 = (iim*nmask).sum()
                df = abs(f0-f1)/f0
                if df<args.tolerance or df <=0:
                    make_bigger = False
                counter += 1
                if counter>args.diter:
                    make_bigger = False
        
                struct = ndimage.generate_binary_structure(2, 2)
                if make_bigger:
                    nmask = morph.binary_dilation(nmask, structure=struct, iterations=1).astype(imask.dtype)
            mask[imslice] = nmask
    
    if args.mask_value != 0:
        if isinstance(mask_value, (str, unicode)):
            if str(mask_value).lower()=="nan":
                mask_value = numpy.nan
        mask[mask==0] = mask_value
    
    hdu[0].data = mask[numpy.newaxis, numpy.newaxis, ...]
    
    hdu.writeto(outname, clobber=True)
    hdu.close()

    logging.info("Sucessfully created binary mask.")
