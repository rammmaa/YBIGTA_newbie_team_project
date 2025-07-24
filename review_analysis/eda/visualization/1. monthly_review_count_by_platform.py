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

df['year_month'] = df['date'].dt.to_period('M').dt.to_timestamp()
monthly_counts = df.groupby(['year_month', 'platform']).size().reset_index(name='review_count')
monthly_counts = monthly_counts.sort_values('year_month')

plt.figure(figsize=(14,7))
sns.barplot(
    data=monthly_counts,
    x='year_month',
    y='review_count',
    hue='platform',
    palette=custom_palette
)
plt.xticks(rotation=45)

ax = plt.gca()
all_ticks = ax.get_xticks()
# 3개월 간격으로 ticks와 labels 선택
ticks = all_ticks[::3]

# year_month가 datetime 이므로 문자열로 변환해서 labels 생성
labels = monthly_counts['year_month'].dt.strftime('%Y-%m').unique()[::3]

ax.set_xticks(ticks)
ax.set_xticklabels(labels)

plt.title('플랫폼별 월별 리뷰 개수')
plt.xlabel('월')
plt.ylabel('리뷰 개수')

plt.legend(title='플랫폼')
plt.tight_layout()
plt.show()


