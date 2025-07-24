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

plt.figure(figsize=(10,6))
sns.boxplot(data=df, x='platform', y='rating', palette="Set2")

plt.title('플랫폼별 별점 분포')
plt.xlabel('플랫폼')
plt.ylabel('별점')
plt.ylim(1, 5)  # 별점 범위 고정
plt.tight_layout()
plt.show()
