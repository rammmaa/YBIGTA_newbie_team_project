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

# 색상 딕셔너리
custom_palette = {
    "Catchtable": "#FFA500",  # 주황
    "Kakaomap": "#FFD700",    # 노랑
    "Googlemap": "#1E90FF"    # 파랑
}

dfs = []
for filepath, platform in files:
    temp_df = pd.read_csv(filepath, parse_dates=['date'])
    temp_df['platform'] = platform
    dfs.append(temp_df)

df = pd.concat(dfs, ignore_index=True)

# 월 단위 컬럼 생성
df['year_month'] = df['date'].dt.to_period('M').dt.to_timestamp()

# 월별, 플랫폼별 평균 별점 계산
monthly_avg_rating = df.groupby(['year_month', 'platform'])['rating'].mean().reset_index()

plt.figure(figsize=(14,7))
sns.lineplot(
    data=monthly_avg_rating,
    x='year_month',
    y='rating',
    hue='platform',
    marker='o',
    palette=custom_palette
)

plt.xticks(rotation=45)
plt.title('플랫폼별 월별 평균 별점 추이')
plt.xlabel('월')
plt.ylabel('평균 별점')
plt.ylim(1, 5)  # 별점 범위 고정

plt.legend(title='플랫폼')
plt.tight_layout()
plt.show()
