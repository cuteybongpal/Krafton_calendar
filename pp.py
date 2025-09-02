# 설치 필요
# pip install easyocr opencv-python

import easyocr
import cv2

# 1. 이미지 읽기 (OpenCV 사용)
image_path = '스크린샷 2025-09-02 213320.png'  # 분석할 이미지 경로
image = cv2.imread(image_path)

# 2. EasyOCR Reader 생성 (한국어, 영어 지원)
reader = easyocr.Reader(['ko', 'en'])

# 3. 이미지에서 텍스트 읽기
results = reader.readtext(image)

# 4. 결과 출력
for (bbox, text, prob) in results:
    print(f"Detected text: {text} (Confidence: {prob:.2f})")

    # 글자 위치 사각형 그리기 (선택 사항)
    top_left = tuple([int(val) for val in bbox[0]])
    bottom_right = tuple([int(val) for val in bbox[2]])
    cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)

# 5. 결과 이미지 확인 (선택 사항)
cv2.imshow('Detected Text', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
