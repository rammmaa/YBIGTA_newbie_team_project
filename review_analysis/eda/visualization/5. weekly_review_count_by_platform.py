import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc

# 한글 폰트 설정 (Mac 기준)
font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)

# 파일 목록과 플랫폼명
files = [
    ("./preprocessed_reviews_catchtable.csv", "Catchtable"),
    ("./preprocessed_reviews_googlemap.csv", "Googlemap"),
    ("./preprocessed_reviews_kakaomap.csv", "Kakaomap")
]

# 플랫폼별 색상 지정
custom_palette = {
    "Catchtable": "#FFA500",  # 주황
    "Kakaomap": "#FFD700",    # 노랑
    "Googlemap": "#1E90FF"    # 파랑
}

# 파일 읽고 병합
dfs = []
for filepath, platform in files:
    temp_df = pd.read_csv(filepath, parse_dates=['date'])
    temp_df['platform'] = platform
    dfs.append(temp_df)

df = pd.concat(dfs, ignore_index=True)

# 요일 이름 설정 (0=월요일 ~ 6=일요일)
weekday_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']

# 요일 컬럼이 없으면 새로 생성
if 'weekday' not in df.columns:
    df['weekday'] = df['date'].dt.weekday  # 0=월요일 ~ 6=일요일

# 시각화
plt.figure(figsize=(10, 6))
sns.countplot(data=df, x='weekday', hue='platform', palette=custom_palette)

plt.title('요일별 리뷰 개수 (플랫폼별)')
plt.xlabel('요일')
plt.ylabel('리뷰 개수')
plt.xticks(ticks=range(7), labels=weekday_names)

plt.legend(title='플랫폼')
plt.tight_layout()
plt.show()
