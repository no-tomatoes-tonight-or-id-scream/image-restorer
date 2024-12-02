import torch
from torchvision import transforms
from PIL import Image
import timm
import csv


def get_row_class(csv_file, rownumber):
    predicted_class_row = []
    with open(csv_file, 'r') as file:
        # 创建csv.reader对象
        reader = csv.reader(file)

        for i, row in enumerate(reader):
            if i == rownumber:
                predicted_class_row = [int(cell) for cell in row]
    print(predicted_class_row)
    return predicted_class_row


def classification(model, image_path):
    image = Image.open(image_path).convert('RGB')

    # 定义图像预处理转换
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # 对图像进行预处理
    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0)  # 添加批次维度

    # 如果有GPU，将模型和输入数据移至GPU
    if torch.cuda.is_available():
        model = model.cuda()
        input_batch = input_batch.cuda()

    # 3. 模型推理
    with torch.no_grad():
        model.eval()  # 设置模型为评估模式
        output = model(input_batch)

    # 4. 解释输出结果
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    predicted_class = torch.argmax(probabilities).item()

    return predicted_class, probabilities[predicted_class].item()


def row(model, image_path, csv_file):
    dataclass = []
    dataprob = []

    for i in range(1, 1001):
        image_path_t = image_path + str(i) + '.png'
        temp_c, temp_p = classification(model, image_path_t)
        dataclass.append(temp_c)
        dataprob.append(temp_p)

    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(dataclass)
        writer.writerow(dataprob)


def adv(model, image_path, row_classes, sur, alg):
    advclass = []
    advprob = []
    success = 0
    num = 0

    for i in range(1, 1001):
        image_path_t = image_path + sur + '\\' + alg + '\\' + str(i) + '.png'
        temp_c, temp_p = classification(model, image_path_t)
        advclass.append(temp_c)
        advprob.append(temp_p)

        if row_classes[i - 1] != advclass[i - 1]:
            success += 1
        num += 1
        print(i)
    print(sur, alg, success / num * 100)


def main():
    surrogate = 'Res_v1_152'
    algorithm = 'FIA'
    csv_file = 'D:\\VersionAS\\row.csv'
    row_image = 'D:\\VersionAS\\FIA\\dataset\\images\\'
    adv_image = 'D:\\VersionAS\\FIA\\adv\\'

    pretrained_cfg_overlay = {'file': r"D:\VersionAS\models\vit_models\vit_huge_patch14_224.orig_in21k.bin"}
    model = timm.models.create_model('vit_huge_patch14_224.orig_in21k', pretrained=True,
                                     pretrained_cfg_overlay=pretrained_cfg_overlay)

    # # 生图分类
    # row(model, row_image, csv_file)

    # 攻击测试
    row_classes = get_row_class(csv_file, 12)
    adv(model, adv_image, row_classes, surrogate, algorithm)


main()
# print(timm.models.create_model('vit_huge_patch14_224.orig_in21k').default_cfg)
# print(timm.list_models('*vit_huge*' , pretrained = True))