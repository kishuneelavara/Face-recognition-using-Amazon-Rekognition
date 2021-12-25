import pandas as pd
import boto3
import io
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont


credential = pd.read_csv("new_user_credentials.csv")
access_key_id = credential['Access key ID'][0]
secret_access_key = credential['Secret access key'][0]

AWS_REKOG = boto3.client('rekognition', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)



def get_bounding_boxes(request):
    response = AWS_REKOG.detect_faces(Image=request, Attributes=['ALL'])
    bounding_boxes = []
    for details in response['FaceDetails']:
        bounding_boxes.append(details['BoundingBox'])
    return bounding_boxes


def face_exists(request):
    response = AWS_REKOG.detect_faces(Image=request, Attributes=['ALL'])
    return response['FaceDetails'] != []


def get_face_name(face, image,COLLECTION_NAME):
    img_width, img_height = image.size
    width = img_width * face['Width']
    height = img_height * face['Height']
    left = img_width * face['Left']
    top = img_height * face['Top']
    area = (left, top, left + width, top + height)
    cropped_image = image.crop(area)
    bytes_array = io.BytesIO()
    cropped_image.save(bytes_array, format="PNG")
    request = {
        'Bytes': bytes_array.getvalue()
    }
    if face_exists(request):
        response = AWS_REKOG.search_faces_by_image(
            CollectionId=COLLECTION_NAME, Image=request, FaceMatchThreshold=70)
        if response['FaceMatches']:
            return response['FaceMatches'][0]['Face']['ExternalImageId']
        else:
            return 'Not recognized'
    return ''


def face_recognition_saving_image(image,COLLECTION_NAME):
    lst=[]
    bytes_array = io.BytesIO()
    image.save(bytes_array, format="PNG")
    request = {
        'Bytes': bytes_array.getvalue()
    }
    bounding_boxes = get_bounding_boxes(request)
    img_width, img_height = image.size
    faces_name = []
    for face in bounding_boxes:
        faces_name.append(get_face_name(face, image,COLLECTION_NAME))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", size=40)
    for i in range(len(bounding_boxes)):
        if not faces_name[i]:
            continue
        width = img_width * bounding_boxes[i]['Width']
        height = img_height * bounding_boxes[i]['Height']
        left = img_width * bounding_boxes[i]['Left']
        top = img_height * bounding_boxes[i]['Top']
        points = ((left, top), (left + width, top), (left + width,
                                                     top + height), (left, top + height), (left, top))
        draw.line(points, fill='#00d400', width=4)
        draw.text((left, top), faces_name[i],font=font)
        print('A face has been recognized. Name: ' + faces_name[i])
        if faces_name[i] =="Not recognized":
            lst.append(faces_name[i] + " face")
        else:
            lst.append('A face has been recognized. Name: ' + faces_name[i])
    # image.save("output.png")
    print('Faces recognition has finished.')
    return image,lst

# if __name__ == '__main__':
#     img="photo1.jpg"
#     source_img = Image.open(img)
#     face_recognition_saving_image(source_img)