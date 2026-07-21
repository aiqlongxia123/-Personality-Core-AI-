"""GMM聚类模块 — 从因子空间中划分人格原型"""
import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score
from .ica_extractor import ICAExtractor


class GMmClusterer:
    """高斯混合模型聚类，将人格分布为不同原型"""

    def __init__(self, n_clusters: int = 6, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.gmm = None
        self.labels_ = None

    def fit(self, factor_scores: np.ndarray) -> "GMmClusterer":
        """训练GMM"""
        self.gmm = GaussianMixture(
            n_components=self.n_clusters,
            random_state=self.random_state,
            covariance_type="full",
        )
        self.labels_ = self.gmm.fit_predict(factor_scores)
        return self

    def predict(self, factor_scores: np.ndarray) -> np.ndarray:
        """预测新数据的聚类标签"""
        if self.gmm is None:
            raise RuntimeError("GMmClusterer未训练，请先调用fit()")
        return self.gmm.predict(factor_scores)

    def get_cluster_centers(self) -> np.ndarray:
        """返回各聚类的中心（在因子空间中）"""
        if self.gmm is None:
            raise RuntimeError("GMmClusterer未训练")
        return self.gmm.means_

    def get_cluster_info(self, archetype_names: list[str]) -> list[dict]:
        """获取每个聚类的详细信息（按簇内多数成员投票命名）"""
        if self.gmm is None or self.labels_ is None:
            raise RuntimeError("GMmClusterer未训练")

        from collections import Counter

        info = []
        for i in range(self.n_clusters):
            mask = self.labels_ == i
            count = int(mask.sum())
            if count == 0:
                continue

            # 按簇内多数成员的实际名字投票命名
            member_indices = np.where(mask)[0]
            member_names = [archetype_names[idx] for idx in member_indices]
            name_counts = Counter(member_names)
            majority_name = name_counts.most_common(1)[0][0]
            purity = name_counts.most_common(1)[0][1] / count

            info.append({
                "cluster_id": i,
                "name": majority_name,
                "size": count,
                "purity": round(purity, 3),
                "center": self.get_cluster_centers()[i].tolist(),
                "members": member_indices.tolist(),
            })
        return info

    @staticmethod
    def find_optimal_clusters(
        factor_scores: np.ndarray,
        k_range: range = range(2, 10),
    ) -> int:
        """用轮廓系数找最优聚类数"""
        best_k = 2
        best_score = -1
        for k in k_range:
            gmm = GaussianMixture(n_components=k, random_state=42)
            labels = gmm.fit_predict(factor_scores)
            if len(set(labels)) < 2:
                continue
            score = silhouette_score(factor_scores, labels)
            if score > best_score:
                best_score = score
                best_k = k
        return best_k
