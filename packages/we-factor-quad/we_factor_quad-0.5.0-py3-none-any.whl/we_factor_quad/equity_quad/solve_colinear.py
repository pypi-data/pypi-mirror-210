import pandas as pd
import numpy as np
from scipy.linalg import block_diag


def get_orthogonal(k_all, k_ind):
    """
    得到一个可以对角化 K_all*K_all维矩阵的正交矩阵，使得对角化后唯一的非零特征值在左上角
    :param k_all: 总维数，即总因子个数
    :param k_ind: 行业因子的维数，即行业因子的个数
    :return: 一个 numpy array 类型的 K_all *K_all维正交矩阵
    """
    assert k_ind > 0, "wrong K_ind: K_ind<=0"

    Orth = [[1 / np.sqrt(k_ind)] * k_ind]
    for i in range(1, k_ind - 1):
        Orth.append([1 / np.sqrt(i * (i + 1))] * i + [-i / np.sqrt(i * (i + 1))] + [0] * (k_ind - 1 - i))
    i = k_ind - 1
    if i > 0:
        Orth.append([1 / np.sqrt(i * (i + 1))] * i + [-i / np.sqrt(i * (i + 1))])
    O = block_diag(*(np.array(Orth), np.identity(k_all - k_ind)))
    return O


def get_sigma_with_country(df_sigma: pd.DataFrame, k_ind: int = 32):
    """
    从不含共线性的 sigma_f 得到添加国家因子的 new_sigma，假设国家因子的因子收益是行业因子收益的平均值
    :param df_sigma: 不包含共线性的Sigma_f, 类型为dataframe, 是不含共线性因子的 variance-covariance matrix, 其columns, index都应为因子名
    :param k_ind: 行业因子的维数，即行业因子的个数
    :return: 与输入的dataframe类似，加入一个国家因子行与列
    """
    columns = list(df_sigma.columns)
    columns.append('country')
    sigma_f = df_sigma.to_numpy()
    l = len(sigma_f)

    X = np.ones((k_ind, k_ind)) / k_ind
    A = block_diag(*(np.identity(k_ind) - X, np.identity(l - k_ind)))
    B = np.array([[1 / k_ind] * k_ind + [0] * (l - k_ind)])
    M = np.concatenate((A, B), axis=0)

    new_sigma = M.dot(sigma_f.dot(M.T))
    return pd.DataFrame(new_sigma, columns=columns, index=columns)


if __name__ == '__main__':
    columns = ['ind1', 'ind2', 'ind3']
    eigen_vals = [0.5, 1.5, 1]
    eigen_vals = np.diag(eigen_vals)
    theta_12 = np.pi / 3
    theta_23 = np.pi / 4
    theta_13 = np.pi / 6
    rot_12 = np.array([[np.cos(theta_12), np.sin(theta_12), 0], [-np.sin(theta_12), np.cos(theta_12), 0], [0, 0, 1]])
    rot_13 = np.array([[np.cos(theta_13), 0, np.sin(theta_13)], [0, 1, 0], [-np.sin(theta_13), 0, np.cos(theta_13)]])
    rot_23 = np.array([[1, 0, 0], [0, np.cos(theta_23), np.sin(theta_23)], [0, -np.sin(theta_23), np.cos(theta_23)]])
    rots = rot_12.dot(rot_13.dot(rot_23))
    M = rots.dot(eigen_vals.dot(rots.T))

    df_sigma = pd.DataFrame(data=M, columns=columns, index=columns)
    df_sigma_new = get_sigma_with_country(df_sigma=df_sigma, k_ind=3)
    print(df_sigma)
    print(df_sigma_new)