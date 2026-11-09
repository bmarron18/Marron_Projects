import numpy as np
import disk

def centroid(data, r, ctr, lim=1., ca=None):
  '''
SYNTAX:
    centroid(data)

PURPOSE:
    This function determines the centroid of an image.

INPUTS:

    data: 2D array containing image values.  Generally, this is a
          portion of a larger image, trimmed so that sources other
          than the one for which a centroid is desired are eliminated.
      
OUTPUTS:
     This function returns an array([cy, cx]) giving the image
     centroid.  For images of point-like objects, the centroid is an
     estimate of the brightness peak.

PROCEDURE:
     The centroiding algorithm follows Section 5.1.1, pp 79-80, of
     Steve B. Howell, Handbook of CCD Astronomy, Cambridge
     University Press, Cambridge, UK, 2000.

EXAMPLE/TEST:

import centroid as c
import gaussian as G
import numpy    as np

npix  = 50
cx    = 28.294
cy    = 32.133
width = 3.2
fakestar = G.gaussian2(np.indices((npix,npix)), (width, width), (cy, cx))
c.centroid(fakestar)
array([ 28.29914645,  32.14229399])
c.centroid(fakestar) - [cx, cy]
array([ 0.00514645,  0.00929399])

MODIFICATION HISTORY:
2003-04-09 0.1	jh@physics.ucf.edu	Initial version in IDL.
2007-10-02 0.2	jh@physics.ucf.edu	Python translation.
2008-10-09 0.3	jh@physics.ucf.edu	Updated to my ctroflight method.
  '''

  if (ca == None):
    ca = np.indices(data.shape)

  wim = data * disk.disk(r, ctr, data.shape)

  if (lim != 1.):
    medval = np.median(wim[np.where(wim != 0)])
    maxval = wim.max()
    wim[np.where(wim < (medval + lim * (maxval - medval)))] = 0

    tim = wim.sum()
    y = (wim * ca[0]).sum() / tim
    x = (wim * ca[1]).sum() / tim

  return np.array([y, x])

def old():
  ny, nx = data.shape
  
  xsum  = np.sum(data, 1)
  ysum  = np.sum(data, 0)
  dmean = np.mean(xsum).astype(float) # dmean = Howell's xmean=ymean if square

  cx =  np.sum( np.clip(xsum - dmean, 0, np.infty) * np.arange(nx)) \
      / np.sum( np.clip(xsum - dmean, 0, np.infty) )

  cy =  np.sum( np.clip(ysum - dmean, 0, np.infty) * np.arange(ny)) \
      / np.sum( np.clip(ysum - dmean, 0, np.infty) )

  return np.array([cy, cx])
