import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc

# 한글 폰트 설정 (Mac 예시)
font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)

files = [
    ("./preprocessed_reviews_catchtable.csv", "Catchtable"),
    ("./preprocessed_reviews_googlemap.csv", "Googlemap"),
    ("./preprocessed_reviews_kakaomap.csv", "Kakaomap")
]

dfs = []
for filepath, platform in files:
    temp_df = pd.read_csv(filepath, parse_dates=['date'])
    temp_df['platform'] = platform
    dfs.append(temp_df)

df = pd.concat(dfs, ignore_index=True)

# 'weekday' 컬럼은 0=월요일 ... 6=일요일 형태라고 가정
weekday_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']

plt.figure(figsize=(10,6))
sns.countplot(data=df, x='weekday', hue='platform', palette='Set2')

plt.title('요일별 리뷰 개수 (플랫폼별)')
plt.xlabel('요일')
plt.ylabel('리뷰 개수')
plt.xticks(ticks=range(7), labels=weekday_names)

plt.legend(title='플랫폼')
plt.tight_layout()
plt.show()
