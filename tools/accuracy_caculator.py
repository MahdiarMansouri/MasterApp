import numpy as np
import cv2 as cv
import torch
from torch.nn import Linear, ReLU, Dropout, Sequential
from torchvision.transforms import transforms
from torchvision.models import vgg11_bn


def acc_calculator(cropped_images):
    # Loading model
    model = vgg11_bn(pretrained=True)
    model.classifier = Sequential(
        Linear(in_features=25088, out_features=4096, bias=True),
        ReLU(inplace=True),
        Dropout(p=0.5, inplace=False),
        Linear(in_features=4096, out_features=4096, bias=True),
        ReLU(inplace=True),
        Dropout(p=0.5, inplace=False),
        Linear(in_features=4096, out_features=2, bias=True))

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    # model_path = 'E:\\PycharmProjects\MainMasterApp\model\DL_models\model_2_13.pth'
    model_path2 = 'E:\\PycharmProjects\MainMasterApp\model\DL_models\model_2.pth'
    model = torch.load(model_path2, map_location=torch.device('cpu'))
    model = model.to(device)

    # transforming images
    transform = transforms.Compose([
        transforms.ToTensor(),
        # transforms.RandomResizedCrop(112)
    ])

    Corallo = 0
    Myxo = 0
    non = 0
    labels = []


    if len(cropped_images) > 12:
        for idx, image in enumerate(cropped_images):
            # print(image.shape)
            dims = np.array(image.shape)
            if dims[0] < 32 or dims[1] < 32:
                transform = transforms.Compose([
                    transforms.ToTensor(),
                    transforms.Resize(32)
                ])
            else:
                transform = transforms.Compose([
                    transforms.ToTensor(),
                    # transforms.Resize(dims.max())
                ])
            image = transform(image)
            image = image.to(device)
            image.unsqueeze_(0)
            model.eval()
            with torch.no_grad():
                output = model(image)
                _, prediction = torch.max(output, 1)
                prob = torch.sigmoid(output)
                percent = prob * 100
                final_percent = float(torch.max(percent, 1)[0])
                if final_percent > 70:
                    if prediction[0] == 0:
                        # print(idx, '=> Corallo')
                        labels.append('Corallo')
                        Corallo += 1
                    else:
                        # print(idx, '=> Myxo')
                        labels.append('Myxo')
                        Myxo += 1
                else:
                    labels.append('NON')
                    non += 1

        # print('Corallo = ', Corallo)
        # print('Myxo = ', Myxo)
        predictions = np.array([Corallo, Myxo])
        result = ((predictions.max() / (predictions[0] + predictions[1])) * 100 ).__round__(2)
        if Corallo > Myxo and Corallo > non:
            predicted_label = 'Corallococcus'
        elif Myxo > Corallo and Myxo > non:
            predicted_label = 'Myxococcus'
        else:
            predicted_label = 'non'
        # predict_label = 'Corallococcus' if Corallo > Myxo else 'Myxococcus'
        # print(result, '%')

        predictions = np.array([Corallo, Myxo, non])
        result = ((predictions.max() / (predictions[0] + predictions[1] + predictions[2])) * 100 ).__round__(2)
        # predict_label = 'Corallococcus' if Corallo > Myxo else 'Myxococcus'
        # print(result, '%')
    else:
        # print('not enough detects...')
        result = 0
        predicted_label = None

    # print('---' * 30)
    return labels, result, predicted_label


