import numpy as np
from model.entity.UNet_model import *
from skimage.transform import resize


def segment(image, transform, shape):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print('your device is: ', device)
    image = transform(image).unsqueeze(0)
    image = image.to(device)

    model = UNet(n_channels=3, n_classes=1)
    model = model.to(device)
    model_path = 'E:\PycharmProjects\MainMasterApp\model\DL_models\detection_unet_model.pth'
    model_weights = torch.load(model_path, map_location=torch.device('cpu'))
    model.load_state_dict(model_weights)
    model.eval()

    with torch.no_grad():
        segmented_image = model(image)
        segmented_image = segmented_image.to('cpu')

    segmented_image = segmented_image.squeeze().numpy()
    segmented_image = (
            255 * (segmented_image - segmented_image.min()) / (segmented_image.ptp()))
    segmented_image = resize(segmented_image, (shape[0], shape[1])).astype(np.uint8)
    return segmented_image


def segment2(image, transform, shape):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print('your device is: ', device)
    image = transform(image).unsqueeze(0)
    image = image.to('cpu')

    model_path = 'E:\PycharmProjects\MainMasterApp\model\DL_models\segmented_model5.pth'
    model = torch.load(model_path, map_location=torch.device('cpu'))
    model.eval()

    with torch.no_grad():
        output = model(image)['out']
        print(output)
        print(output.shape)

        pred = torch.argmax(output, dim=1)
        print(pred)
        segmented_image = pred.squeeze().cpu().numpy()
        print(segmented_image)

    segmented_image = (
            255 * (segmented_image - segmented_image.min()) / (segmented_image.ptp()))
    segmented_image = resize(segmented_image, (shape[0], shape[1])).astype(np.uint8)
    # print(pred)
    return segmented_image
