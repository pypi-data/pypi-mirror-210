import os
import argparse
import numpy as np


from omero.gateway import BlitzGateway
from ezomero import post_dataset, post_image, ezimport

from biom3d.utils import adaptive_imread, abs_listdir, tif_copy_meta, adaptive_imsave

def omero_dataset_upload(conn, pred_dir, img_dir, project_id, ext="_predictions"):
    """Create a novel Omero dataset with the name of the prediction directory and upload the predictions in it.
    """
    # create the new dataset
    dataset_name = os.path.basename(img_dir)
    if len(dataset_name)==0: # this might happen if pred_dir=='path/to/folder/'
        dataset_name = os.path.basename(os.path.dirname(img_dir))
    dataset_name += ext
    dataset_id = post_dataset(
        conn,
        dataset_name,
        project_id,
        )

    # replace the metadata of pred by img
    pred_files = abs_listdir(pred_dir)
    img_files = abs_listdir(img_dir)

    assert len(pred_files)==len(img_files), "[Error] Not the same number of predictions and images."

    print("Copying file metadata...")
    # for i in range(len(pred_files)):
    #     print(pred_files[i])
        # # add eventually missing dimension in predictions
        # img = adaptive_imread(pred_files[i])[0]

        # assert len(img.shape)>=2 or len(img.shape)>5, "[Error] Strange image shape..."

        # # expand image dim is needed
        # if len(img.shape)<5:
        #     print("Too few dimension in image of shape", img.shape, "Some dimension will be added to match ZYXCT")
        #     if len(img.shape)==4: # move the channel axis to the end
        #         img = np.moveaxis(img, 0, -1)
        #     missing_dim = tuple(np.arange(len(img.shape),5))
        #     img = np.expand_dims(img, missing_dim)
        
        # # save back the image
        # adaptive_imsave(pred_files[i], img)

        # copy the metadata of the original image into the output image
        # tif_copy_meta(img_files[i], pred_files[i], out_path=pred_files[i])
    print("Done copying!")
    
    print("Uploading images...")
    # upload the images in the new dataset
    for i in range(len(pred_files)): 
        # TODO: does not work!!!
        ezimport(
            conn=conn,
            target=pred_files[i],
            dataset=dataset_id,
            ln_s=True,
        )

        # post_image(
        #     conn=conn,
        #     image=img,
        #     image_name=os.path.basename(pred_files[i]), 
        #     dataset_id=dataset_id,
        #     # source_image_id=653587,
        #     dim_order='zyxct'
        #     )
    print("Done uploading!")

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Omero uploader. ONLY FOR DATASET, NOT FOR PROJECT.")
    parser.add_argument('--project_id', type=int,
        help="Id of Project in which to create the Dataset. If no Project is specified, the Dataset will be orphaned.")
    parser.add_argument('--pred_dir',
        help="Directory of the predictions.")
    parser.add_argument('--img_dir',
        help="Directory name of the original images. Used to upload the correct meta-data in the prediction.")
    parser.add_argument('--username',
        help="User name")
    parser.add_argument('--password',
        help="Password")
    parser.add_argument('--hostname',
        help="Host name")
    args = parser.parse_args()

    conn = BlitzGateway(args.username, args.password, host=args.hostname, port=4064)
    conn.connect()

    omero_dataset_upload(conn, args.pred_dir, args.img_dir, args.project_id)

    # img = adaptive_imread(args.img_path)[0]
    # img = np.expand_dims(img, (3,4))

    # print(img.shape)
    # post_image(
    #     conn=conn,
    #     image=img,
    #     image_name=os.path.basename(args.img_path), 
    #     dataset_id=26616,
    #     # source_image_id=653587,
    #     dim_order='zyxct'
    #     )

    conn.close()