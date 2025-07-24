import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from matplotlib import font_manager, rc

# 한글 폰트 설정 (Mac 예시)
font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)

def str_to_vec(s):
    """벡터 문자열을 numpy 배열로 변환"""
    return np.array(ast.literal_eval(s))

def main():
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

    # vector 컬럼 문자열 -> numpy 배열 변환
    df['vec_array'] = df['vector'].apply(str_to_vec)

    # 벡터 행렬 생성
    vectors = np.stack(df['vec_array'].values)

    # t-SNE 2D 변환 (시간 걸릴 수 있음)
    tsne = TSNE(n_components=2, random_state=42)
    vec_2d = tsne.fit_transform(vectors)

    df['tsne_x'] = vec_2d[:, 0]
    df['tsne_y'] = vec_2d[:, 1]

    # KMeans 클러스터링 (5개 군집)
    kmeans = KMeans(n_clusters=5, random_state=42)
    df['cluster'] = kmeans.fit_predict(vectors)

    # t-SNE 산점도 (별점 색깔)
    plt.figure(figsize=(10,8))
    scatter = plt.scatter(df['tsne_x'], df['tsne_y'], c=df['rating'], cmap='viridis', alpha=0.6)
    plt.colorbar(scatter, label='별점')
    plt.title('Word2Vec 임베딩 t-SNE 2D 시각화 (별점 색깔)')
    plt.xlabel('t-SNE 축 1')
    plt.ylabel('t-SNE 축 2')
    plt.tight_layout()
    plt.show()

    # t-SNE 산점도 + 클러스터링 색깔
    plt.figure(figsize=(10,8))
    sns.scatterplot(data=df, x='tsne_x', y='tsne_y', hue='cluster', palette='Set2', alpha=0.7)
    plt.title('Word2Vec 임베딩 t-SNE + KMeans 클러스터링')
    plt.xlabel('t-SNE 축 1')
    plt.ylabel('t-SNE 축 2')
    plt.legend(title='클러스터')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
