import cv2 as cv


def detect(segmented_image, image, labels=None, label_annotate=False):
    ret, binary_mask_thresh = cv.threshold(segmented_image, 150, 255, cv.THRESH_BINARY)
    contours, hierarchy = cv.findContours(binary_mask_thresh, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    # if label_annotate == False:
        # print('Contours count:', len(contours))
    cropped_images = []
    for_crop_image = image.copy()

    cnt_idx = 0

    for cnt in contours:
        area = cv.contourArea(cnt)
        if area > 50:
            x, y, w, h = cv.boundingRect(cnt)
            cropped_img = for_crop_image[y:y + h, x:x + w]
            cropped_images.append(cropped_img)
            # print(cropped_img.shape)
            # print(cropped_img.shape[0] * cropped_img.shape[1])
            if label_annotate and len(labels) != 0:
                if labels[cnt_idx] == 'NON':
                    color = (36, 36, 255)
                elif labels[cnt_idx] == 'Corallo':
                    color = (36, 255, 12)
                else:
                    color = (255, 36, 36)
                # color = (36, 255, 12) if labels[cnt_idx] == 'Corallo' else (255, 12, 12)
                cv.rectangle(image, (x, y), (x + w, y + h), color, 2)
                cv.putText(image, labels[cnt_idx], (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cnt_idx += 1


    return binary_mask_thresh, image, cropped_images
