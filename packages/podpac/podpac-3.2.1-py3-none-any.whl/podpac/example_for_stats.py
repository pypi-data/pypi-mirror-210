import matplotlib.pyplot as plt
import xarray as xr
import numpy as np

import podpac
import soilmap.datalib.geowatch as geowatch


with podpac.settings:
    # Cache so I only have to fetch data from the server once (or twice??)
    podpac.settings["DEFAULT_CACHE"] = ["ram", "disk"]
    podpac.settings["MULTITHREADING"] = False
    # Make a set of fine and coarse coordinates
    # Center coordinates about Creare
    center_lat, center_lon = 43.682102, -72.233455
    # get deltas using 110 km / deg and a 30 x 30 km box
    f_box_lat_lon = 30 / 2 / 110
    n_fine = int(30 / (30 / 1000))  # Number of 30 m boxes in a 30km square (hint, it's 1000)
    n_coarse = 3
    f_coords =  podpac.Coordinates([
        podpac.clinspace(center_lat + f_box_lat_lon, center_lat - f_box_lat_lon, n_fine),
        podpac.clinspace(center_lon - f_box_lat_lon, center_lon + f_box_lat_lon, n_fine),
            ["2022-06-01T12"]], ["lat", "lon", "time"]
    )
    c_coords = f_coords[::333, ::333]

    # make the coordinates for the brute-force technique
    e1 = podpac.algorithm.ExpandCoordinates(time=["0,D", "30,D", '1,D'])
    day_time_coords = podpac.Coordinates([e1.get_modified_coordinates1d(f_coords, 'time')])
    e2 = podpac.algorithm.ExpandCoordinates(source=e1, time=["-4,Y", "0,Y", '1,Y'])
    all_time_coords = podpac.Coordinates([e2.get_modified_coordinates1d(day_time_coords, 'time')])

    all_f_coords = podpac.coordinates.merge_dims([f_coords.drop('time'), all_time_coords])
    all_c_coords = podpac.coordinates.merge_dims([c_coords.drop('time'), all_time_coords])

    # Also, use the average of the vegetation, for initial testing
    sm = geowatch.SoilMoisture()
    o_veg = []
    vegetation = sm.vegetation
    one_month_coords = all_f_coords[:, :, :32*5:5]
    shape = one_month_coords[:, :, :32*5:5].shape
    shape = (shape[0], shape[1], 1)  # set maximum time shape to 1
    for coords in one_month_coords.iterchunks(shape):
        o_veg.append(vegetation.eval(coords))
    o_veg = xr.concat(o_veg, 'time')
    veg_node = podpac.data.Array(source=o_veg.mean('time').data, coordinates=all_f_coords.drop('time'))


    # Quick test to make sure everything makes sense
    sm = geowatch.SoilMoisture()
    sm_ca = sm.solmst_0_10
    sm_cr = sm.relsolmst_0_10  # you can compute this from the abs soil moisture above... but I'm lazy so I'll just get this data for now
    o_fine = sm.eval(f_coords)
    o_coarse = sm_ca.eval(c_coords)
    o_coarse2 = sm_ca.eval(f_coords)
    plt.subplot(221)
    o_fine.plot(vmin=0, vmax=0.5)
    plt.subplot(222)
    o_coarse.plot(vmin=0, vmax=0.5)
    plt.subplot(224)
    o_coarse2.plot(vmin=0, vmax=0.5)
    plt.show()

    # Now let's get ALL the data needed for a brute-force approach and the elegant cheap approach
    # get the data for brute-force
    # TODO: Need to fix the WCS node so we can tell it just to fetch 1 timepoint at a time -- in that case we
    # could have just use e2 above to get the data
    all_f_data = []
    shape = all_f_coords.shape
    shape = (shape[0], shape[1], 1)  # set maximum time shape to 1
    all_fine_time_abs_data = []
    all_fine_time_rel_data = []
    for coords in all_f_coords.iterchunks(shape):
        all_fine_time_abs_data.append(sm_ca.eval(coords))
        all_fine_time_rel_data.append(sm_cr.eval(coords))

    all_f_data = xr.concat(all_f_data, 'time')

    # get the data for the cheap approach
    all_ca_data = []
    all_cr_data = []
    shape = all_c_coords.shape
    shape = (shape[0], shape[1], 1)  # set maximum time shape to 1
    for coords in all_c_coords.iterchunks(shape):
        all_ca_data.append(sm_ca.eval(coords))
        all_cr_data.append(sm_cr.eval(coords))
    all_ca_data = xr.concat(all_ca_data, 'time')
    all_cr_data = xr.concat(all_cr_data, 'time')

    # compute the histograms for the coarse-scale data
    n_bins = 32  # We can change this!
    new_shape = all_ca_data.shape[:2] + (n_bins,)
    new_shape_edges = all_ca_data.shape[:2] + (n_bins + 1,)
    all_ca_pdfs = np.zeros((new_shape))
    all_ca_edges = np.zeros((new_shape_edges))
    all_cr_pdfs = np.zeros((new_shape))
    all_cr_edges = np.zeros((new_shape_edges))
    for i in range(new_shape[0]):
        for j in range(new_shape[1]):
            tmp = all_ca_data.data[i, j].ravel()
            tmp = tmp[np.isfinite(tmp)]
            all_ca_pdfs[i, j, :], all_ca_edges[i, j, :] = np.histogram(tmp, density=True, bins=n_bins)
            tmp = all_cr_data.data[i, j].ravel()
            tmp = tmp[np.isfinite(tmp)]
            all_cr_pdfs[i, j, :], all_cr_edges[i, j, :] = np.histogram(tmp, density=True, bins=n_bins)

    # Check on one of these
    assert np.abs(1 - (all_ca_pdfs[1, 1] * (all_ca_edges[1, 1][1:] - all_ca_edges[1, 1][:-1])).sum()) < 1e-14
    plt.stairs(all_ca_pdfs[1, 1], all_ca_edges[1, 1], fill=True)
    plt.stairs(all_ca_pdfs[1, 1], all_ca_edges[1, 1], color='k', fill=False)
    plt.show()

    # Compute the centers -- this is making the data we'll use for g(x)
    all_ca_centers = (all_ca_edges[..., 1:] + all_ca_edges[..., :-1]) * 0.5
    all_cr_centers = (all_cr_edges[..., 1:] + all_cr_edges[..., :-1]) * 0.5

    # We're finally where Clay was with his Code. *Whew*. Now the part
    # that wasn't that obvious... how to construct g(x)?
    # NEed to fake coordinates for the fake data nodes
    stats_coords_f = all_f_coords[:, :, :n_bins * 2:2]
    stats_coords = all_c_coords[:, :, :n_bins * 2:2]
    abs_ws_stats = podpac.data.Array(
        source=all_ca_centers, # Here's the weatherscale data at the centers of the bins
        coordinates=stats_coords,  # Mock the coordinates
        interpolation="bilinear"
    )
    rel_ws_stats = podpac.data.Array(
        source=all_cr_centers,
        coordinates=stats_coords,  # Mock the coordinates
        interpolation="bilinear"
    )

    # Make the g(x) function
    sm_stats = geowatch.SoilMoisture(solmst_0_10=abs_ws_stats, relsolmst_0_10=rel_ws_stats, vegetation=veg_node)
    # Evaluate g(x)
    stats_f_data = []
    shape = stats_coords_f.shape
    shape = (shape[0], shape[1], 1)  # set maximum time shape to 1
    for coords in stats_coords_f.iterchunks(shape):
        stats_f_data.append(sm_stats.eval(coords))  # should be fast -- all local cached data (Except vegetation for some reason? )
    stats_f_data = xr.concat(stats_f_data, 'time')

    # Now the part we've al been waiting for, computing the mean
    # First we have to interpolate the coarse-scale data
    # edges
    ca_edges = podpac.data.Array(
        source=all_ca_edges,
        coordinates=all_c_coords[:, :, :n_bins + 1],  # Again, the time coordinate here is fake -- I just want to interpolate space
        interpolation='bilinear'
    )
    ca_edges_f = ca_edges.eval(all_f_coords[:, :, :n_bins + 1])
    # pdfs
    ca_pdfs = podpac.data.Array(
        source=all_ca_pdfs,
        coordinates=all_c_coords[:, :, :n_bins],  # Again, the time coordinate here is fake -- I just want to interpolate space
        interpolation='bilinear'
    )
    ca_pdfs_f = ca_pdfs.eval(all_f_coords[:, :, :n_bins])
    # Compute the mean
    truth_mean = all_f_data.mean('time').data
    cheap_mean = (stats_f_data.data * ca_pdfs_f.data * (ca_edges_f[..., 1:].data - ca_edges_f[..., :-1].data)).sum(axis=-1)
    # TODO: compute the variance (maybe like this? )
    # cheap_x2 = (stats_f_data.data**2 * ca_pdfs_f.data * (ca_edges_f[..., 1:].data - ca_edges_f[..., :-1].data)).sum(axis=-1)
    # cheap_std = np.sqrt(cheap_x2 - cheap_mean ** 2)

    # Plot results
    plt.figure()
    kwargs = dict(vmin=0.1, vmax=0.4)
    ax1 = plt.subplot(131)
    plt.imshow(truth_mean, **kwargs)
    plt.title("Truth")
    plt.colorbar()
    plt.subplot(132, sharex=ax1, sharey=ax1)
    plt.imshow(cheap_mean, **kwargs)
    plt.title(f"Cheap,Approx, nbins={n_bins}")
    plt.colorbar()
    plt.subplot(133, sharex=ax1, sharey=ax1)
    plt.title("Cheap - Truth")
    plt.imshow(cheap_mean - truth_mean, cmap='BrBG')#, vmin=-0.02, vmax=0.02)
    plt.colorbar()
    plt.show()

    # Also plot a few pdfs, just for interest sake (can we construct these with the cheap method?)
    plt.figure()
    dry_pixel = (544, 466)
    avg_pixel = (333,600)
    wet_pixel = (749, 479)
    # wet_pixel = (529, 79)
    kwargs = dict(bins=n_bins, density=True, alpha=0.5)
    plt.stairs(all_ca_pdfs[1, 1], all_ca_edges[1, 1], fill=True, label="weatherscale")
    plt.hist(all_f_data[dry_pixel], label='dry', **kwargs)
    plt.hist(all_f_data[wet_pixel], label='wet', **kwargs)
    plt.hist(all_f_data[avg_pixel], label='avg', **kwargs)
    plt.legend()
    plt.show()
