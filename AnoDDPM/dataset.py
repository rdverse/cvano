import os
from random import randint

import cv2
import nibabel as nib
import numpy as np
import torch
from matplotlib import animation
from torch.utils.data import Dataset
from torchvision import datasets, transforms


# helper function to make getting another batch of data easier


# from diffusion_training import output_img


def cycle(iterable):
    while True:
        for x in iterable:
            yield x


def make_pngs_anogan():
    dir = {
        "Train":     "./DATASETS/Train", "Test": "./DATASETS/Test",
        "Anomalous": "./DATASETS/CancerousDataset/EdinburghDataset/Anomalous-T1"
        }
    slices = {
        "17904": range(165, 205), "18428": range(177, 213), "18582": range(160, 190), "18638": range(160, 212),
        "18675": range(140, 200), "18716": range(135, 190), "18756": range(150, 205), "18863": range(130, 190),
        "18886": range(120, 180), "18975": range(170, 194), "19015": range(158, 195), "19085": range(155, 195),
        "19275": range(184, 213), "19277": range(158, 209), "19357": range(158, 210), "19398": range(164, 200),
        "19423": range(142, 200), "19567": range(160, 200), "19628": range(147, 210), "19691": range(155, 200),
        "19723": range(140, 170), "19849": range(150, 180)
        }
    center_crop = 235
    import os
    try:
        os.makedirs("./DATASETS/AnoGAN")
    except OSError:
        pass
    # for d_set in ["Train", "Test"]:
    #     try:
    #         os.makedirs(f"./DATASETS/AnoGAN/{d_set}")
    #     except OSError:
    #         pass
    #
    #     files = os.listdir(dir[d_set])
    #
    #     for volume_name in files:
    #         try:
    #             volume = np.load(f"{dir[d_set]}/{volume_name}/{volume_name}.npy")
    #         except (FileNotFoundError, NotADirectoryError) as e:
    #             continue
    #         for slice_idx in range(40, 120):
    #             image = volume[:, slice_idx:slice_idx + 1, :].reshape(256, 192).astype(np.float32)
    #             image = (image * 255).astype(np.int32)
    #             empty_image = np.zeros((256, center_crop))
    #             empty_image[:, 21:213] = image
    #             image = empty_image
    #             center = (image.shape[0] / 2, image.shape[1] / 2)
    #
    #             x = center[1] - center_crop / 2
    #             y = center[0] - center_crop / 2
    #             image = image[int(y):int(y + center_crop), int(x):int(x + center_crop)]
    #             image = cv2.resize(image, (64, 64))
    #             cv2.imwrite(f"./DATASETS/AnoGAN/{d_set}/{volume_name}-slice={slice_idx}.png", image)

    try:
        os.makedirs(f"./DATASETS/AnoGAN/Anomalous")
    except OSError:
        pass
    try:
        os.makedirs(f"./DATASETS/AnoGAN/Anomalous-mask")
    except OSError:
        pass
    files = os.listdir(f"{dir['Anomalous']}/raw_cleaned")
    center_crop = (175, 240)
    for volume_name in files:
        try:
            volume = np.load(f"{dir['Anomalous']}/raw_cleaned/{volume_name}")
            volume_mask = np.load(f"{dir['Anomalous']}/mask_cleaned/{volume_name}")
        except (FileNotFoundError, NotADirectoryError) as e:
            continue
        temp_range = slices[volume_name[:-4]]
        for slice_idx in np.linspace(temp_range.start + 5, temp_range.stop - 5, 4).astype(np.uint16):
            image = volume[slice_idx, ...].reshape(volume.shape[1], volume.shape[2]).astype(np.float32)
            image = (image * 255).astype(np.int32)
            empty_image = np.zeros((max(volume.shape[1], center_crop[0]), max(volume.shape[2], center_crop[1])))

            empty_image[9:165, :] = image
            image = empty_image
            center = (image.shape[0] / 2, image.shape[1] / 2)

            x = center[1] - center_crop[1] / 2
            y = center[0] - center_crop[0] / 2
            image = image[int(y):int(y + center_crop[0]), int(x):int(x + center_crop[1])]
            image = cv2.resize(image, (64, 64))
            cv2.imwrite(f"./DATASETS/AnoGAN/Anomalous/{volume_name}-slice={slice_idx}.png", image)

            image = volume_mask[slice_idx, ...].reshape(volume.shape[1], volume.shape[2]).astype(np.float32)
            image = (image * 255).astype(np.int32)
            empty_image = np.zeros((max(volume.shape[1], center_crop[0]), max(volume.shape[2], center_crop[1])))

            empty_image[9:165, :] = image
            image = empty_image
            center = (image.shape[0] / 2, image.shape[1] / 2)

            x = center[1] - center_crop[1] / 2
            y = center[0] - center_crop[0] / 2
            image = image[int(y):int(y + center_crop[0]), int(x):int(x + center_crop[1])]
            image = cv2.resize(image, (64, 64))
            cv2.imwrite(f"./DATASETS/AnoGAN/Anomalous-mask/{volume_name}-slice={slice_idx}.png", image)




def main(save_videos=True, bias_corrected=False, verbose=0):
    DATASET = "./DATASETS/CancerousDataset/EdinburghDataset"
    patients = os.listdir(DATASET)
    for i in [f"{DATASET}/Anomalous-T1/raw_new", f"{DATASET}/Anomalous-T1/mask_new"]:
        try:
            os.makedirs(i)
        except OSError:
            pass
    if save_videos:
        for i in [f"{DATASET}/Anomalous-T1/raw_new/videos", f"{DATASET}/Anomalous-T1/mask_new/videos"]:
            try:
                os.makedirs(i)
            except OSError:
                pass

    for patient in patients:
        try:
            patient_data = os.listdir(f"{DATASET}/{patient}")
        except:
            if verbose:
                print(f"{DATASET}/{patient} Not a directory")
            continue
        for data_folder in patient_data:
            if "COR_3D" in data_folder:
                try:
                    T1_files = os.listdir(f"{DATASET}/{patient}/{data_folder}")
                except:
                    if verbose:
                        print(f"{patient}/{data_folder} not a directory")
                    continue
                try:
                    mask_dir = os.listdir(f"{DATASET}/{patient}/tissue_classes")
                    for file in mask_dir:
                        if file.startswith("cleaned") and file.endswith(".nii"):
                            mask_file = file
                except:
                    if verbose:
                        print(f"{DATASET}/{patient}/tissue_classes dir not found")
                    return
                for t1 in T1_files:
                    if bias_corrected:
                        check = t1.endswith("corrected.nii")
                    else:
                        check = t1.startswith("anon")
                    if check and t1.endswith(".nii"):
                        # try:
                        # use slice 35-55
                        img = nib.load(f"{DATASET}/{patient}/{data_folder}/{t1}")
                        mask = nib.load(f"{DATASET}/{patient}/tissue_classes/{mask_file}").get_fdata()
                        image = img.get_fdata()
                        if verbose:
                            print(image.shape)
                        if bias_corrected:
                            # image.shape = (256, 156, 256)
                            image = np.rot90(image, 3, (0, 2))
                            image = np.flip(image, 1)
                            # image.shape = (256, 156, 256)
                        else:
                            image = np.transpose(image, (1, 2, 0))
                        mask = np.transpose(mask, (1, 2, 0))
                        if verbose:
                            print(image.shape)
                        image_mean = np.mean(image)
                        image_std = np.std(image)
                        img_range = (image_mean - 1 * image_std, image_mean + 2 * image_std)
                        image = np.clip(image, img_range[0], img_range[1])
                        image = image / (img_range[1] - img_range[0])

                        np.save(
                                f"{DATASET}/Anomalous-T1/raw_new/{patient}.npy", image.astype(
                                        np.float32
                                        )
                                )
                        np.save(
                                f"{DATASET}/Anomalous-T1/mask_new/{patient}.npy", mask.astype(
                                        np.float32
                                        )
                                )
                        if verbose:
                            print(f"Saved {DATASET}/Anomalous-T1/mask/{patient}.npy")

                        if save_videos:
                            fig = plt.figure()
                            ims = []
                            for i in range(image.shape[0]):
                                tempImg = image[i:i + 1, :, :]
                                im = plt.imshow(
                                        tempImg.reshape(image.shape[1], image.shape[2]), cmap='gray', animated=True
                                        )
                                ims.append([im])

                            ani = animation.ArtistAnimation(
                                    fig, ims, interval=50, blit=True,
                                    repeat_delay=1000
                                    )

                            ani.save(f"{DATASET}/Anomalous-T1/raw_new/videos/{patient}.mp4")
                            if verbose:
                                print(f"Saved {DATASET}/Anomalous-T1/raw/videos/{patient}.mp4")
                            fig = plt.figure()
                            ims = []
                            for i in range(mask.shape[0]):
                                tempImg = mask[i:i + 1, :, :]
                                im = plt.imshow(
                                        tempImg.reshape(mask.shape[1], mask.shape[2]), cmap='gray', animated=True
                                        )
                                ims.append([im])

                            ani = animation.ArtistAnimation(
                                    fig, ims, interval=50, blit=True,
                                    repeat_delay=1000
                                    )

                            ani.save(f"{DATASET}/Anomalous-T1/mask_new/videos/{patient}.mp4")
                            if verbose:
                                print(mask.shape)
                                print(f"Saved {DATASET}/Anomalous-T1/raw/videos/{patient}.mp4")


def checkDataSet():
    resized = False
    mri_dataset = AnomalousMRIDataset(
            "DATASETS/CancerousDataset/EdinburghDataset/Anomalous-T1/raw", img_size=(256, 256),
            slice_selection="iterateUnknown", resized=resized
            # slice_selection="random"
            )

    dataset_loader = cycle(
            torch.utils.data.DataLoader(
                    mri_dataset,
                    batch_size=22, shuffle=True,
                    num_workers=2, drop_last=True
                    )
            )

    new = next(dataset_loader)

    image = new["image"]

    print(image.shape)
    from helpers import gridify_output
    print("Making Video for resized =", resized)
    fig = plt.figure()
    ims = []
    for i in range(0, image.shape[1], 2):
        tempImg = image[:, i, ...].reshape(image.shape[0], 1, image.shape[2], image.shape[3])
        im = plt.imshow(
                gridify_output(tempImg, 5), cmap='gray',
                animated=True
                )
        ims.append([im])

    ani = animation.ArtistAnimation(
            fig, ims, interval=50, blit=True,
            repeat_delay=1000
            )

    ani.save(f"./CancerousDataset/EdinburghDataset/Anomalous-T1/video-resized={resized}.mp4")


def output_videos_for_dataset():
    folders = os.listdir("/Users/jules/Downloads/19085/")
    folders.sort()
    print(f"Folders: {folders}")
    for folder in folders:
        try:
            files_folder = os.listdir("/Users/jules/Downloads/19085/" + folder)
        except:
            print(f"{folder} not a folder")
            exit()

        for file in files_folder:
            try:
                if file[-4:] == ".nii":
                    # try:
                    # use slice 35-55
                    img = nib.load("/Users/jules/Downloads/19085/" + folder + "/" + file)
                    image = img.get_fdata()
                    image = np.rot90(image, 3, (0, 2))
                    print(f"{folder}/{file} has shape {image.shape}")
                    outputImg = np.zeros((256, 256, 310))
                    for i in range(image.shape[1]):
                        tempImg = image[:, i:i + 1, :].reshape(image.shape[0], image.shape[2])
                        img_sm = cv2.resize(tempImg, (310, 256), interpolation=cv2.INTER_CUBIC)
                        outputImg[i, :, :] = img_sm

                    image = outputImg
                    print(f"{folder}/{file} has shape {image.shape}")
                    fig = plt.figure()
                    ims = []
                    for i in range(image.shape[0]):
                        tempImg = image[i:i + 1, :, :]
                        im = plt.imshow(tempImg.reshape(image.shape[1], image.shape[2]), cmap='gray', animated=True)
                        ims.append([im])

                    ani = animation.ArtistAnimation(
                            fig, ims, interval=50, blit=True,
                            repeat_delay=1000
                            )

                    ani.save("/Users/jules/Downloads/19085/" + folder + "/" + file + ".mp4")
                    plt.close(fig)

            except:
                print(
                        f"--------------------------------------{folder}/{file} FAILED TO SAVE VIDEO ------------------------------------------------"
                        )



def load_datasets_for_test():
    args = {'img_size': (256, 256), 'random_slice': True, 'Batch_Size': 20}
    training, testing = init_datasets("./", args)

    ano_dataset = AnomalousMRIDataset(
            ROOT_DIR=f'DATASETS/CancerousDataset/EdinburghDataset/Anomalous-T1', img_size=args['img_size'],
            slice_selection="random", resized=False
            )

    train_loader = init_dataset_loader(training, args)
    ano_loader = init_dataset_loader(ano_dataset, args)

    for i in range(5):
        new = next(train_loader)
        new_ano = next(ano_loader)
        output = torch.cat((new["image"][:10], new_ano["image"][:10]))
        plt.imshow(helpers.gridify_output(output, 5), cmap='gray')
        plt.show()
        plt.pause(0.0001)


def init_datasets(ROOT_DIR, args):
    training_dataset = MRIDataset(
            ROOT_DIR=f'{ROOT_DIR}DATASETS/Train/', img_size=args['img_size'], random_slice=args['random_slice']
            )
    testing_dataset = MRIDataset(
            ROOT_DIR=f'{ROOT_DIR}DATASETS/Test/', img_size=args['img_size'], random_slice=args['random_slice']
            )
    return training_dataset, testing_dataset


def init_dataset_loader(mri_dataset, args, shuffle=True):
    dataset_loader = cycle(
            torch.utils.data.DataLoader(
                    mri_dataset,
                    batch_size=args['Batch_Size'], shuffle=shuffle,
                    num_workers=0, drop_last=True
                    )
            )

    return dataset_loader


class DAGM(Dataset):
    def __init__(self, dir, anomalous=False, img_size=(256, 256), rgb=False, random_crop=True):
        # dir = './DATASETS/Carpet/Class1'
        if anomalous and dir[-4:] != "_def":
            dir += "_def"
        self.ROOT_DIR = dir
        self.anomalous = anomalous
        if rgb:
            norm_const = ((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        else:
            norm_const = ((0.5), (0.5))

        if random_crop:
            self.transform = transforms.Compose(
                    [
                        transforms.ToPILImage(),
                        transforms.ToTensor(),
                        transforms.Normalize(*norm_const)
                        ]
                    )
        else:
            self.transform = transforms.Compose(
                    [
                        transforms.ToPILImage(),
                        transforms.Resize(img_size, transforms.InterpolationMode.BILINEAR),
                        transforms.ToTensor(),
                        transforms.Normalize(*norm_const)
                        ]
                    )
        self.rgb = rgb
        self.img_size = img_size
        self.random_crop = random_crop
        if anomalous:
            self.coord_info = self.load_coordinates(os.path.join(self.ROOT_DIR, "labels.txt"))
        self.filenames = os.listdir(self.ROOT_DIR)
        for i in self.filenames[:]:
            if not i.endswith(".png"):
                self.filenames.remove(i)
        self.filenames = sorted(self.filenames, key=lambda x: int(x[:-4]))

    def load_coordinates(self, path_to_coor):
        '''
        '''

        coord_dict_all = {}
        with open(path_to_coor) as f:
            coordinates = f.read().split('\n')
            for coord in coordinates:
                # print(len(coord.split('\t')))
                if len(coord.split('\t')) == 6:
                    coord_dict = {}
                    coord_split = coord.split('\t')
                    # print(coord_split)
                    # print('\n')
                    coord_dict['major_axis'] = round(float(coord_split[1]))
                    coord_dict['minor_axis'] = round(float(coord_split[2]))
                    coord_dict['angle'] = float(coord_split[3])
                    coord_dict['x'] = round(float(coord_split[4]))
                    coord_dict['y'] = round(float(coord_split[5]))
                    index = int(coord_split[0]) - 1
                    coord_dict_all[index] = coord_dict

        return coord_dict_all

    def make_mask(self, idx, img):
        mask = np.zeros_like(img)
        mask = cv2.ellipse(
                mask,
                (int(self.coord_info[idx]['x']), int(self.coord_info[idx]['y'])),
                (int(self.coord_info[idx]['major_axis']), int(self.coord_info[idx]['minor_axis'])),
                (self.coord_info[idx]['angle'] / 4.7) * 270,
                0,
                360,
                (255, 255, 255),
                -1
                )

        mask[mask > 0] = 255
        return mask

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):

        # print(repr(idx))
        if torch.is_tensor(idx):
            idx = idx.tolist()
        sample = {"filenames": self.filenames[idx]}
        if self.rgb:
            sample["image"] = cv2.imread(os.path.join(self.ROOT_DIR, self.filenames[idx]), 1)
            # sample["image"] = Image.open(os.path.join(self.ROOT_DIR, self.filenames[idx]), "r")
        else:
            sample["image"] = cv2.imread(os.path.join(self.ROOT_DIR, self.filenames[idx]), 0)

        if self.anomalous:
            sample["mask"] = self.make_mask(int(self.filenames[idx][:-4]) - 1, sample["image"])
        if self.random_crop:
            x1 = randint(0, sample["image"].shape[-1] - self.img_size[1])
            y1 = randint(0, sample["image"].shape[-2] - self.img_size[0])
            if self.anomalous:
                sample["mask"] = sample["mask"][x1:x1 + self.img_size[1], y1:y1 + self.img_size[0]]
            sample["image"] = sample["image"][x1:x1 + self.img_size[1], y1:y1 + self.img_size[0]]

        if self.transform:
            image = self.transform(sample["image"])
            if self.anomalous:
                sample["mask"] = self.transform(sample["mask"])
                sample["mask"] = (sample["mask"] > 0).float()
        sample["image"] = image.reshape(1, *self.img_size)

        return sample


class MVTec(Dataset):
    def __init__(self, dir, anomalous=False, img_size=(256, 256), rgb=True, random_crop=True, include_good=False):
        # dir = './DATASETS/leather'

        self.ROOT_DIR = dir
        self.anomalous = anomalous
        if not anomalous:
            self.ROOT_DIR += "/train/good"

        transforms_list = [transforms.ToPILImage()]

        if rgb:
            channels = 3
        else:
            channels = 1
            transforms_list.append(transforms.Grayscale(num_output_channels=channels))
        transforms_mask_list = [transforms.ToPILImage(), transforms.Grayscale(num_output_channels=channels)]
        if not random_crop:
            transforms_list.append(transforms.Resize(img_size, transforms.InterpolationMode.BILINEAR))
            transforms_mask_list.append(transforms.Resize(img_size, transforms.InterpolationMode.BILINEAR))
        transforms_list.append(transforms.ToTensor())
        transforms_mask_list.append(transforms.ToTensor())
        if rgb:
            transforms_list.append(transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)))
        else:
            transforms_list.append(transforms.Normalize((0.5), (0.5)))
        transforms_mask_list.append(transforms.Normalize((0.5), (0.5)))
        self.transform = transforms.Compose(transforms_list)
        self.transform_mask = transforms.Compose(transforms_mask_list)

        self.rgb = rgb
        self.img_size = img_size
        self.random_crop = random_crop
        self.classes = ["color", "cut", "fold", "glue", "poke"]
        if include_good:
            self.classes.append("good")
        if anomalous:
            self.filenames = [f"{self.ROOT_DIR}/test/{i}/{x}" for i in self.classes for x in
                              os.listdir(self.ROOT_DIR + f"/test/{i}")]

        else:
            self.filenames = [f"{self.ROOT_DIR}/{i}" for i in os.listdir(self.ROOT_DIR)]

        for i in self.filenames[:]:
            if not i.endswith(".png"):
                self.filenames.remove(i)
        self.filenames = sorted(self.filenames, key=lambda x: int(x[-7:-4]))

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        # print(repr(idx))
        if torch.is_tensor(idx):
            idx = idx.tolist()
        sample = {"filenames": self.filenames[idx]}
        if self.rgb:
            sample["image"] = cv2.cvtColor(cv2.imread(os.path.join(self.filenames[idx]), 1), cv2.COLOR_BGR2RGB)
            # sample["image"] = Image.open(os.path.join(self.ROOT_DIR, self.filenames[idx]), "r")
        else:
            sample["image"] = cv2.imread(os.path.join(self.filenames[idx]), 0)
            sample["image"] = sample["image"].reshape(*sample["image"].shape, 1)

        if self.anomalous:
            file = self.filenames[idx].split("/")
            if file[-2] == "good":
                sample["mask"] = np.zeros((sample["image"].shape[0], sample["image"].shape[1], 1)).astype(np.uint8)
            else:
                sample["mask"] = cv2.imread(
                        os.path.join(self.ROOT_DIR, "ground_truth", file[-2], file[-1][:-4] + "_mask.png"), 0
                        )
        if self.random_crop:
            x1 = randint(0, sample["image"].shape[-2] - self.img_size[1])
            y1 = randint(0, sample["image"].shape[-3] - self.img_size[0])
            if self.anomalous:
                sample["mask"] = sample["mask"][x1:x1 + self.img_size[1], y1:y1 + self.img_size[0]]
            sample["image"] = sample["image"][x1:x1 + self.img_size[1], y1:y1 + self.img_size[0]]

        if self.transform:
            sample["image"] = self.transform(sample["image"])
            if self.anomalous:
                sample["mask"] = self.transform_mask(sample["mask"])
                sample["mask"] = (sample["mask"] > 0).float()

        return sample



class MRIDataset(Dataset):
    """Healthy MRI dataset."""

    def __init__(self, ROOT_DIR, transform=None, img_size=(32, 32), random_slice=False):
        """
        Args:
            ROOT_DIR (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.transform = transforms.Compose(
                [transforms.ToPILImage(),
                 transforms.RandomAffine(3, translate=(0.02, 0.09)),
                 transforms.CenterCrop(235),
                 transforms.Resize(img_size, transforms.InterpolationMode.BILINEAR),
                 # transforms.CenterCrop(256),
                 transforms.ToTensor(),
                 transforms.Normalize((0.5), (0.5))
                 ]
                ) if not transform else transform

        self.filenames = os.listdir(ROOT_DIR)
        if ".DS_Store" in self.filenames:
            self.filenames.remove(".DS_Store")
        self.ROOT_DIR = ROOT_DIR
        self.random_slice = random_slice

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        # print(repr(idx))
        if torch.is_tensor(idx):
            idx = idx.tolist()
        if os.path.exists(os.path.join(self.ROOT_DIR, self.filenames[idx], f"{self.filenames[idx]}.npy")):
            image = np.load(os.path.join(self.ROOT_DIR, self.filenames[idx], f"{self.filenames[idx]}.npy"))
            pass
        else:
            img_name = os.path.join(
                    self.ROOT_DIR, self.filenames[idx], f"sub-{self.filenames[idx]}_ses-NFB3_T1w.nii.gz"
                    )
            # random between 40 and 130
            # print(nib.load(img_name).slicer[:,90:91,:].dataobj.shape)
            img = nib.load(img_name)
            image = img.get_fdata()

            image_mean = np.mean(image)
            image_std = np.std(image)
            img_range = (image_mean - 1 * image_std, image_mean + 2 * image_std)
            image = np.clip(image, img_range[0], img_range[1])
            image = image / (img_range[1] - img_range[0])
            np.save(
                    os.path.join(self.ROOT_DIR, self.filenames[idx], f"{self.filenames[idx]}.npy"), image.astype(
                            np.float32
                            )
                    )
        if self.random_slice:
            # slice_idx = randint(32, 122)
            slice_idx = randint(40, 100)
        else:
            slice_idx = 80

        image = image[:, slice_idx:slice_idx + 1, :].reshape(256, 192).astype(np.float32)

        if self.transform:
            image = self.transform(image)

        sample = {'image': image, "filenames": self.filenames[idx]}
        return sample


class AnomalousMRIDataset(Dataset):
    """Anomalous MRI dataset."""

    def __init__(
            self, ROOT_DIR, transform=None, img_size=(32, 32), slice_selection="random", resized=False,
            cleaned=True
            ):
        """
        Args:
            ROOT_DIR (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
            img_size: size of each 2D dataset image
            slice_selection: "random" = randomly selects a slice from the image
                             "iterateKnown" = iterates between ranges of tumour using slice data
                             "iterateUnKnown" = iterates through whole MRI volume
        """
        self.transform = transforms.Compose(
                [transforms.ToPILImage(),
                 transforms.CenterCrop((175, 240)),
                 # transforms.RandomAffine(0, translate=(0.02, 0.1)),
                 transforms.Resize(img_size, transforms.InterpolationMode.BILINEAR),
                 # transforms.CenterCrop(256),
                 transforms.ToTensor(),
                 transforms.Normalize((0.5), (0.5))
                 ]
                ) if not transform else transform
        self.img_size = img_size
        self.resized = resized
        self.slices = {
            "17904": range(165, 205), "18428": range(177, 213), "18582": range(160, 190), "18638": range(160, 212),
            "18675": range(140, 200), "18716": range(135, 190), "18756": range(150, 205), "18863": range(130, 190),
            "18886": range(120, 180), "18975": range(170, 194), "19015": range(158, 195), "19085": range(155, 195),
            "19275": range(184, 213), "19277": range(158, 209), "19357": range(158, 210), "19398": range(164, 200),
            "19423": range(142, 200), "19567": range(160, 200), "19628": range(147, 210), "19691": range(155, 200),
            "19723": range(140, 170), "19849": range(150, 180)
            }

        self.filenames = self.slices.keys()
        if cleaned:
            self.filenames = list(map(lambda name: f"{ROOT_DIR}/raw_cleaned/{name}.npy", self.filenames))
        else:
            self.filenames = list(map(lambda name: f"{ROOT_DIR}/raw/{name}.npy", self.filenames))
        # self.filenames = os.listdir(ROOT_DIR)
        if ".DS_Store" in self.filenames:
            self.filenames.remove(".DS_Store")
        self.ROOT_DIR = ROOT_DIR
        self.slice_selection = slice_selection

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        if os.path.exists(os.path.join(f"{self.filenames[idx]}")):
            if self.resized and os.path.exists(os.path.join(f"{self.filenames[idx][:-4]}-resized.npy")):
                image = np.load(os.path.join(f"{self.filenames[idx][:-4]}-resized.npy"))
            else:
                image = np.load(os.path.join(f"{self.filenames[idx]}"))
        else:
            img_name = os.path.join(self.filenames[idx])
            # print(nib.load(img_name).slicer[:,90:91,:].dataobj.shape)
            img = nib.load(img_name)
            image = img.get_fdata()
            image = np.rot90(image)

            image_mean = np.mean(image)
            image_std = np.std(image)
            img_range = (image_mean - 1 * image_std, image_mean + 2 * image_std)
            image = np.clip(image, img_range[0], img_range[1])
            image = image / (img_range[1] - img_range[0])
            np.save(
                    os.path.join(f"{self.filenames[idx]}.npy"), image.astype(
                            np.float32
                            )
                    )
        sample = {}

        if self.resized:
            img_mask = np.load(f"{self.ROOT_DIR}/mask/{self.filenames[idx][-9:-4]}-resized.npy")
        else:
            img_mask = np.load(f"{self.ROOT_DIR}/mask/{self.filenames[idx][-9:-4]}.npy")
        if self.slice_selection == "random":
            temp_range = self.slices[self.filenames[idx][-9:-4]]
            slice_idx = randint(temp_range.start, temp_range.stop)
            image = image[slice_idx:slice_idx + 1, :, :].reshape(image.shape[1], image.shape[2]).astype(np.float32)
            if self.transform:
                image = self.transform(image)
                # image = transforms.functional.rotate(image, -90)
            sample["slices"] = slice_idx
        elif self.slice_selection == "iterateKnown":
            temp_range = self.slices[self.filenames[idx][-9:-4]]
            output = torch.empty(temp_range.stop - temp_range.start, *self.img_size)
            output_mask = torch.empty(temp_range.stop - temp_range.start, *self.img_size)

            for i, val in enumerate(temp_range):
                temp = image[val, ...].reshape(image.shape[1], image.shape[2]).astype(np.float32)
                temp_mask = img_mask[val, ...].reshape(image.shape[1], image.shape[2]).astype(np.float32)
                if self.transform:
                    temp = self.transform(temp)
                    temp_mask = self.transform(temp_mask)
                output[i, ...] = temp
                output_mask[i, ...] = temp_mask

            image = output
            sample["slices"] = temp_range
            sample["mask"] = (output_mask > 0).float()

        elif self.slice_selection == "iterateKnown_restricted":

            temp_range = self.slices[self.filenames[idx][-9:-4]]
            output = torch.empty(4, *self.img_size)
            output_mask = torch.empty(4, *self.img_size)
            slices = np.linspace(temp_range.start + 5, temp_range.stop - 5, 4).astype(np.int32)
            for counter, i in enumerate(slices):
                temp = image[i, ...].reshape(image.shape[1], image.shape[2]).astype(np.float32)
                temp_mask = img_mask[i, ...].reshape(image.shape[1], image.shape[2]).astype(np.float32)
                if self.transform:
                    temp = self.transform(temp)
                    temp_mask = self.transform(temp_mask)
                output[counter, ...] = temp
                output_mask[counter, ...] = temp_mask
            image = output
            sample["slices"] = slices
            sample["mask"] = (output_mask > 0).float()

        elif self.slice_selection == "iterateUnknown":

            output = torch.empty(image.shape[0], *self.img_size)
            for i in range(image.shape[0]):
                temp = image[i:i + 1, :, :].reshape(image.shape[1], image.shape[2]).astype(np.float32)
                if self.transform:
                    temp = self.transform(temp)
                    # temp = transforms.functional.rotate(temp, -90)
                output[i, ...] = temp

            image = output
            sample["slices"] = image.shape[0]

        sample["image"] = image
        sample["filenames"] = self.filenames[idx]
        # sample = {'image': image, "filenames": self.filenames[idx], "slices":slice_idx}
        return sample


def load_CIFAR10(args, train=True):
    return torch.utils.data.DataLoader(
            datasets.CIFAR10(
                    "./DATASETS/CIFAR10", train=train, download=True, transform=transforms
                        .Compose(
                            [
                                transforms.ToTensor(),
                                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))

                                ]
                            )
                    ),
            shuffle=True, batch_size=args["Batch_Size"], drop_last=True
            )


if __name__ == "__main__":
    # load_datasets_for_test()
    # get_segmented_labels(True)
    # main(False, False, 0)
    # make_pngs_anogan()
    import matplotlib.pyplot as plt
    import helpers

    d_set = MVTec(
            './DATASETS/leather', True, img_size=(256, 256), rgb=False
            )
    # d_set = AnomalousMRIDataset(
    #         ROOT_DIR='./DATASETS/CancerousDataset/EdinburghDataset/Anomalous-T1', img_size=(256, 256),
    #         slice_selection="iterateKnown_restricted", resized=False
    #         )
    loader = init_dataset_loader(d_set, {"Batch_Size": 16})

    for i in range(4):
        new = next(loader)
        plt.imshow(helpers.gridify_output(new["image"], 4), cmap="gray")
        plt.show()
        plt.imshow(helpers.gridify_output(new["mask"], 4), cmap="gray")
        plt.show()
        plt.pause(1)
