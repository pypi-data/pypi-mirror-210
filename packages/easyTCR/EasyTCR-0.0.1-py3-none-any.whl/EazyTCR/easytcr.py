import os, re, time
import numpy as np
import pandas as pd
from plotnine import *
import seaborn as sns
import matplotlib.pyplot as plt
from copy import deepcopy
from typing import Callable, Union, Tuple
from scipy.spatial.distance import squareform


def load_test():
    return np.load('test_data.npy')

# 导入数据
def tcr_load(filepath, process=True):
    """
    Example:
                    count          frac    vgene    jgene            cdr3aa
              0     120167  2.580886e-02   TRBV30  TRBJ2-7     CAWSRPPVHEQYF
              1     118090  2.536277e-02  TRBV6-1  TRBJ2-2   CASSEWQGLTGELFF
              2     113159  2.430372e-02    TRBV2  TRBJ1-1     CASRGGVGTEAFF
              3     107877  2.316927e-02   TRBV27  TRBJ2-2    CASSFCRVSGELFF
              4      95114  2.042810e-02  TRBV6-1  TRBJ2-7  CASSAVVGGALNEQYF
    """
    data = []
    sample = []
    for _, _, filenames in os.walk(filepath):
        for filename in filenames:
            temp_data = pd.read_table(os.path.join(filepath, filename))
            if process:
                print('Loading ---------- {}'.format(filename))
            temp_data = temp_data.rename(columns={'cloneCount': 'count',
                                                  'cloneFraction': 'frac',
                                                  'allVHitsWithScore': 'vgene',
                                                  'allJHitsWithScore': 'jgene',
                                                  #                                                   'nSeqCDR3': 'cdr3nt',
                                                  'aaSeqCDR3': 'cdr3aa'})
            del_idx = []  # 保存不符合格式TCR的索引
            for j, i in enumerate(temp_data['cdr3aa']):
                if re.search('[^ACDEFGHIKLMNPQRSTVWY]', i):
                    del_idx.append(j)
            temp_data = temp_data.drop(del_idx).reset_index(drop=True)
            temp_data['vgene'] = temp_data['vgene'].apply(lambda x: x.split('*')[0])
            temp_data['jgene'] = temp_data['jgene'].apply(lambda x: x.split('*')[0])
            temp_data['frac'] = temp_data[['frac']].apply(lambda x: x / x.sum())
            temp_data = temp_data.groupby(['vgene', 'jgene', 'cdr3aa'])[['frac', 'count']].sum().reset_index()
            temp_data = temp_data.sort_values(by='frac', ascending=False).reset_index(drop=True)
            data.append(temp_data)
            sample.append(filename.split('.')[0])
        print('Everything is ok!')
    return data, sample


def label_load(filepath, process=True):
    '''
    Example:
                  index sample status effective sex
            0    P1-BIO     P1    Bio         P   M
            1   P1-POST     P1   Post         P   M
            2   P10-BIO    P10    Bio         N   M
            3  P10-POST    P10   Post         N   M
            4   P11-BIO    P11    Bio         P   F
    '''
    print(f'Reading Done!')
    return pd.read_csv(filepath)


TCRANA_METHOD = ['all', 'unique', 'abundance', 'length']


class TCRAna:

    def __init__(self):
        pass

    def get_result(self, tcr_data, method='unique'):
        if method not in TCRANA_METHOD:
            raise AttributeError(f'Input right method{TCRANA_METHOD}')
        if method == 'all':
            return self.all_clone(tcr_data)
        if method == 'unique':
            return self.unique_clone(tcr_data)
        elif method == 'abundance':
            return self.clone_abundance(tcr_data)
        else:
            return self.cdr3_length(tcr_data)

    def get_plot(self, tcr_data, method='unique', label_data=None, by=None, show_L=True, xlog=True, ylog=True):
        if method not in TCRANA_METHOD:
            raise AttributeError(f'Input right method{TCRANA_METHOD}')
        if method == 'unique':
            if label_data is None and by is not None:
                raise AttributeError(f'Input label data before setting by')
            else:
                return self.plot_unique_data(tcr_data, label_data, by, show_L)
        elif method == 'abundance':
            return self.plot_clone_abundance(tcr_data, xlog, ylog, show_L)
        else:
            return self.plot_cdr3_length(tcr_data, show_L)

    def unique_clone(self, tcr_data):
        return pd.DataFrame([len(i.drop_duplicates()) for i in tcr_data[0]], index=tcr_data[1],
                            columns=['uni_clone']).reset_index()

    def clone_abundance(self, tcr_data):
        clone_num = pd.DataFrame()
        for i, j in enumerate(tcr_data[0]):
            temp_count = pd.DataFrame(j['count'].value_counts().reset_index())
            temp_count = temp_count.assign(Sample=tcr_data[1][i])
            clone_num = pd.concat([clone_num, temp_count], axis=0)
        return clone_num.reset_index(drop=True).rename(columns={'index': 'Abundance', 'count': 'Count'})

    def cdr3_length(self, tcr_data):
        cdr3_len = pd.DataFrame()
        for i, j in enumerate(tcr_data[0]):
            temp_len = pd.DataFrame(j['cdr3aa'].apply(lambda x: len(x)).value_counts().reset_index())
            temp_len = temp_len.assign(Sample=tcr_data[1][i])
            cdr3_len = pd.concat([cdr3_len, temp_len], axis=0)
        return cdr3_len.reset_index(drop=True).rename(columns={'cdr3aa': 'count'})

    def plot_unique_data(self, tcr_data, label_data, by, show_L):
        uni_data = self.unique_clone(tcr_data)
        if uni_data.shape[0] < 10:
            fig_s = 10
        else:
            fig_s = uni_data.shape[0] / 3
        if label_data is None:
            base_plot = (ggplot(uni_data, aes('index', 'uni_clone'))
                         + geom_bar(aes(fill='index'), stat='identity', width=0.8, colour='black', size=.25,
                                    show_legend=show_L)
                         #                         +geom_text(aes(label='uni_clone'),position=position_dodge(width=.75), size=8, va='bottom')
                         + theme_bw() + theme(figure_size=(fig_s, 6.5), axis_text_x=element_text(angle=90, hjust=1)))
        else:
            # 获取输入元素label
            if by is None:
                by = label_data.columns[1]
            if by not in label_data.columns:
                raise AttributeError(f"'DataFrame' object has no attribute '{by}'")
            uni_data = pd.merge(uni_data, label_data)
            base_plot = (ggplot(uni_data, aes(x='index', y='uni_clone', fill=by))
                         + geom_bar(stat='identity', color='black', position='dodge', width=0.7, size=.25,
                                    show_legend=show_L)
                         #                         +geom_text(aes(label='uni_clone'),position=position_dodge(width=.75), size=8, va='bottom')
                         + theme_bw() + theme(figure_size=(fig_s, 6.5), axis_text_x=element_text(angle=90, hjust=0.5)))
        return base_plot + xlab('Sample') + ylab('Number of unique clone')

    def plot_clone_abundance(self, tcr_data, xlog, ylog, show_L):
        clone_ab = self.clone_abundance(tcr_data)
        base_plot = (ggplot(clone_ab, aes(x='Abundance', y='Count', fill='Sample')) + geom_line(aes(color='Sample'),
                                                                                                show_legend=show_L) + theme_bw() + theme(
            axis_text=element_text(size=30, color='black'),
            axis_title=element_text(size=30, color='black'), axis_text_x=element_text(angle=30, vjust=1, hjust=1)))
        if xlog:
            base_plot = base_plot + scale_x_log10()
        if ylog:
            base_plot = base_plot + scale_y_log10()
        return base_plot

    def plot_cdr3_length(self, tcr_data, show_L):
        length_data = self.cdr3_length(tcr_data)
        base_plot = (ggplot(length_data, aes(x='index', y='count', fill='Sample'))
                     + geom_bar(stat='identity', color='black', position='dodge', width=0.7, size=.25,
                                show_legend=show_L)
                     + theme_classic() + xlab('Length of CDR3') + ylab('Count') + theme(
                    axis_text=element_text(size=30, color='black'), plot_title=element_text(size=25),
                    axis_title=element_text(size=30, color='black')) + labs(title='Distribution of CDR3 lengths',
                                                                            y='Clones', x=''))
        return base_plot


TCRCLONA_METHOD = ['dxx_prop', 'top', 'down', 'cate_spec']


class TCRClona:

    def __init__(self):
        pass

    def get_result(self, tcr_data, method='dxx_prop', xx=20, list_bins_top=[0, 10, 100, 1000, 5000, 10000, np.inf],
                   list_bins_down=[1, 5, 10, 25, 100, np.inf], list_bins_cate_spec=[0, 1e-6, 1e-5, 1e-4, 0.01, 1]):
        if method not in TCRCLONA_METHOD:
            raise AttributeError(f'Input right method{TCRCLONA_METHOD}')
        if method == 'dxx_prop':
            return self.dxx_prop(tcr_data, xx=xx)
        elif method == 'top':
            return self.top_data(tcr_data, list_bins_top)
        elif method == 'down':
            return self.down_data(tcr_data, list_bins_down)
        else:
            list_labels = ['Rare', 'Small', 'Medium', 'Large', 'Hyper']
            list_labels = [f'{list_labels[i]}({list_bins_cate_spec[i]}<X<={list_bins_cate_spec[i + 1]})' for i in
                           range(len(list_labels))]
            return self.cate_spec_data(tcr_data, list_bins_cate_spec, list_labels)

    def get_plot(self, tcr_data, method='dxx_prop', xx=20, comp=True,
                 list_bins_top=[0, 10, 100, 1000, 5000, 10000, np.inf], list_bins_down=[1, 5, 10, 25, 100, np.inf],
                 list_bins_cate_spec=[0, 1e-6, 1e-5, 1e-4, 0.01, 1]):
        if method not in TCRCLONA_METHOD:
            raise AttributeError(f'Input right method{TCRCLONA_METHOD}')
        if method == 'dxx_prop':
            return self.plot_dxx_prop(tcr_data, xx=xx, comp=comp)
        elif method == 'top':
            return self.plot_top_data(tcr_data, list_bins_top)
        elif method == 'down':
            return self.plot_down_data(tcr_data, list_bins_down)
        else:
            list_labels = ['Rare', 'Small', 'Medium', 'Large', 'Hyper']
            list_labels = [f'{list_labels[i]}({list_bins_cate_spec[i]}<X<={list_bins_cate_spec[i + 1]})' for i in
                           range(len(list_labels))]
            return self.plot_cate_spec_data(tcr_data, list_bins_cate_spec, list_labels)

    def dxx_prop(self, tcr_data, xx):
        prop = [np.cumsum(i['frac'].values) for i in tcr_data[0]]
        return pd.DataFrame([[np.abs(i - xx / 100).argmin() + 1 for i in prop], tcr_data[1]],
                            index=['d' + str(xx) + '_num', 'label']).T

    def top_data(self, tcr_data, list_bins):
        tcr_data = tcr_data
        top_df = pd.DataFrame()
        for tcr, sample in zip(tcr_data[0], tcr_data[1]):
            tcr = tcr.assign(
                Indices=pd.cut(tcr.index, bins=list_bins, right=False, labels=None, retbins=False, precision=3,
                               include_lowest=True))
            tcr = pd.DataFrame(tcr.groupby('Indices').sum()['frac']).reset_index()
            tcr['frac'] = tcr[['frac']].apply(lambda x: x / x.sum())
            tcr = tcr.assign(Sample=sample)
            top_df = pd.concat([top_df, tcr], axis=0)
        return top_df.reset_index(drop=True)

    def down_data(self, tcr_data, list_bins):
        down_df = pd.DataFrame()
        for tcr, sample in zip(tcr_data[0], tcr_data[1]):
            tcr = tcr.assign(
                Indices=pd.cut(tcr['count'], bins=list_bins, right=False, labels=None, retbins=False, precision=3,
                               include_lowest=True))
            tcr = pd.DataFrame(tcr['Indices'].value_counts(sort=False)).reset_index()
            tcr['Indices'] = tcr[['Indices']].apply(lambda x: x / x.sum())
            tcr = tcr.assign(Sample=sample)
            down_df = pd.concat([down_df, tcr], axis=0)

        return down_df.reset_index(drop=True).rename(columns={'index': 'Indices', 'Indices': 'frac'})

    def cate_spec_data(self, tcr_data, list_bins, list_labels):
        cate_df = pd.DataFrame()
        for tcr, sample in zip(tcr_data[0], tcr_data[1]):
            tcr = tcr.assign(Indices=pd.cut(tcr['frac'], bins=list_bins, right=False, labels=list_labels, retbins=False,
                                            precision=3))
            tcr = pd.DataFrame(tcr['Indices'].value_counts(sort=False)).reset_index()
            tcr['Indices'] = tcr[['Indices']].apply(lambda x: x / x.sum())
            tcr = tcr.assign(Sample=sample)
            cate_df = pd.concat([cate_df, tcr], axis=0)

        return cate_df.reset_index(drop=True).rename(columns={'index': 'Group', 'Indices': 'frac'})

    def plot_dxx_prop(self, tcr_data, xx, comp):
        dxx_data = self.dxx_prop(tcr_data, xx=xx)
        dxx_data.columns = ['count', 'Sample']
        fig_s = dxx_data['Sample'].nunique() / 3
        if not comp:
            base_plot = (ggplot(dxx_data, aes('Sample', 'count'))
                         + geom_bar(aes(fill='Sample'), stat='identity', width=0.8, colour='black', size=.25)
                         + theme_bw() + theme(figure_size=(fig_s, 6.5)))
        else:
            dxx_data['sample'] = dxx_data['Sample'].apply(lambda x: x.split('-')[0])
            dxx_data['label'] = dxx_data['Sample'].apply(lambda x: x.split('-')[1])
            base_plot = (ggplot(dxx_data, aes(x='sample', y='count', fill='label'))
                         + geom_bar(stat='identity', color='black', position='dodge', width=.8, size=.25)
                         + scale_fill_manual(values=['#F8766D', '#00BFC4'])
                         + theme_bw() + theme(figure_size=(fig_s, 6.5)))
        return base_plot + xlab('Sample') + ylab('D' + str(xx) + ' Clone')

    def plot_top_data(self, tcr_data, list_bins):
        top_df = self.top_data(tcr_data, list_bins)
        fig_s = top_df['Sample'].nunique() / 3
        base_plot = (ggplot(top_df, aes('Sample', 'frac', fill='Indices'))
                     + geom_bar(stat='identity', color='black', position='stack', width=0.8, size=0.25)
                     + scale_fill_brewer(palette='YlOrRd') + theme_bw()
                     + theme(figure_size=(fig_s, 6.5), axis_text_x=element_text(angle=90, hjust=1)) + ylab('Frac'))
        return base_plot

    def plot_down_data(self, tcr_data, list_bins):
        down_df = self.down_data(tcr_data, list_bins)
        fig_s = down_df['Sample'].nunique() / 3
        base_plot = (ggplot(down_df, aes('Sample', 'frac', fill='Indices'))
                     + geom_bar(stat='identity', color='black', position='stack', width=0.8, size=0.25)
                     + scale_fill_brewer(type='qualitative', palette='Set1') + theme_bw() + theme(
                    figure_size=(fig_s, 6.5), axis_text_x=element_text(angle=90, hjust=1)) + ylab('Frac'))
        return base_plot

    def plot_cate_spec_data(self, tcr_data, list_bins, list_labels):
        cate_df = self.cate_spec_data(tcr_data, list_bins, list_labels)
        fig_s = cate_df['Sample'].nunique() / 3
        base_plot = (ggplot(cate_df, aes('Sample', 'frac', fill='Group'))
                     + geom_bar(stat='identity', color='black', position='stack', width=0.8, size=0.25)
                     + scale_fill_brewer(palette='Blues') + theme_bw() + theme(figure_size=(fig_s, 6.5),
                                                                               axis_text_x=element_text(angle=90,
                                                                                                        hjust=1)) + ylab(
                    'Frac'))
        return base_plot


class TCRGene:

    def __init__(self):
        pass

    def get_result(self, tcr_data, method='all', name=None):
        if method == 'all':
            return self.gene_usage(tcr_data)

    def get_plot(self, tcr_data, method='all', name=None, maxlabel=5, maxshow=30):
        self.name = name
        if method == 'all':
            return self.plot_gene_usage(tcr_data, maxshow=maxshow, maxlabel=maxlabel)

    def gene_usage(self, tcr_data):
        #         col_names = data.columns.tolist()
        gene_dict = {}
        for tcr, sample in zip(tcr_data[0], tcr_data[1]):
            gene_dict[sample] = pd.DataFrame(tcr[['vgene', 'jgene']].value_counts(), columns=['num']).reset_index()
        return gene_dict

    def _gapped_ribbons(self,
                        data: list,
                        *,
                        ax: Union[plt.axes, list, None] = None,
                        xstart: float = 1.2,
                        gapfreq: float = 1.0,
                        gapwidth: float = 0.4,
                        ribcol: Union[str, Tuple, None] = None,
                        fun: Callable = lambda x: x[3]
                                                  + (x[4] / (1 + np.exp(-((x[5] / x[2]) * (x[0] - x[1]))))),
                        figsize: Tuple[float, float] = (3.44, 2.58),
                        dpi: int = 300,
                        ) -> plt.Axes:
        '''
        Inspired by Scirpy.
        '''

        if ax is None:
            fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        else:
            if isinstance(ax, list):
                ax = ax[0]

        spread = 10
        xw = gapfreq - gapwidth
        slope = xw * 0.8
        x, y1, y2 = [], [], []
        for i in range(1, len(data)):
            xmin = xstart + (i - 1) * gapfreq
            tx = np.linspace(xmin, xmin + xw, 100)
            xshift = xmin + xw / 2
            p1, p2 = data[i - 1]
            p3, p4 = data[i]
            ty1 = fun((tx, xshift, slope, p1, p3 - p1, spread))
            ty2 = fun((tx, xshift, slope, p2, p4 - p2, spread))
            x += tx.tolist()
            y1 += ty1.tolist()
            y2 += ty2.tolist()
            x += np.linspace(xmin + xw, xstart + i * gapfreq, 10).tolist()
            y1 += np.zeros(10).tolist()
            y2 += np.zeros(10).tolist()
        if ribcol is None:
            ax.fill_between(x, y1, y2, alpha=0.6)
        else:
            ax.fill_between(x, y1, y2, color=ribcol, alpha=0.6)

        return ax

    def plot_gene_usage(self, tcr_data, maxshow=5, maxlabel=30):
        '''
        maxshow:默认显示最多30个连接线
        '''
        data = tcr_data[['vgene', 'jgene']]
        col_names = data.columns.tolist()
        fig, ax = plt.subplots(figsize=(2, 2), dpi=300)
        color_list = {col: dict() for col in col_names}
        bar_list = {col: dict() for col in col_names}
        for col_idx, col_name in enumerate(col_names):
            df = pd.DataFrame(data[col_name].value_counts())
            bottom = 0
            genes = df.index.tolist()
            for i in range(df.shape[0])[::-1]:
                bar_colors = ax.bar(col_idx + 1, df.loc[genes[i], col_name], width=0.4, bottom=bottom,
                                    edgecolor='black')
                color_list[col_name][genes[i]] = bar_colors.patches[-1].get_facecolor()
                bar_list[col_name][genes[i]] = df.loc[genes[i], col_name] + bottom
                if i < maxlabel:
                    if col_name == 'jgene':
                        ax.text(
                            1 + col_idx - 0.4 / 2 + 0.05,
                            bottom + 100,
                            genes[i].split('B')[1],
                            size=7
                        )
                    else:
                        ax.text(
                            1 + col_idx - 0.4 / 2 + 0.05,
                            bottom + 50,
                            genes[i].split('B')[1],
                            size=7
                        )

                bottom += df.loc[genes[i], col_name]

        gene_connect = pd.DataFrame(data[col_names].value_counts()).reset_index()
        bar_list_tmp = deepcopy(bar_list)
        for _, i in gene_connect.iloc[:maxshow, :].iterrows():
            connect_breakpoints = []
            height = i[0]
            connect_color = color_list[col_names[0]][i[col_names[0]]]
            for col_name in col_names:
                gene = i[col_name]
                top = bar_list_tmp[col_name][gene]
                connect_breakpoints.append((top - height, top))
                bar_list_tmp[col_name][gene] = top - height
            self._gapped_ribbons(
                connect_breakpoints,
                ax=ax,
                gapwidth=0.4,
                xstart=1.2,
                ribcol=connect_color,
            )
        ax.set_xticks(range(1, len(col_names) + 1))
        ax.set_xticklabels(['Vgene', 'Jgene'])
        ax.set_yticks([])

    #         ax.set_title( )
    #         plt.savefig('./test_img/'+self.name+'.png')

    def plot_cdr3_transfer(self, tcr_data, tcr_sample, maxshow=30):
        data = tcr_data[['vgene', 'jgene']]
        col_names = data.columns.tolist()
        max_len = col_names[0] if data[col_names[0]].nunique() > data[col_names[1]].nunique() else col_names[1]
        fig, ax = plt.subplots(figsize=(4, 4), dpi=300)
        color_list = {col: dict() for col in col_names}
        bar_list = {col: dict() for col in col_names}
        for col_idx, col_name in enumerate(col_names):

            df = pd.DataFrame(data[col_name].value_counts()).reset_index().sort_values('index').reset_index()
            #             df['code'] = df['index'].cat.codes
            df['code'] = [i for i in range(df.shape[0])]
            bottom = 0
            genes = df.index.tolist()
            labels_name = ['A', 'B', 'C', 'D', 'E', 'F']
            legend_name = ['[0.0, 10.0)', '[10.0, 100.0)', '[100.0, 1000.0)', '[1000.0, 5000.0)', '[5000.0, 10000.0)',
                           '[10000.0, inf)'][::-1]
            for i in range(df.shape[0])[::-1]:
                if col_name == max_len:
                    bar_colors = ax.bar(col_idx + 1, df[col_name][df['code'] == i], width=0.4, bottom=bottom,
                                        edgecolor='black', color='C' + str(i), label=legend_name[df.shape[0] - i - 1])
                else:

                    bar_colors = ax.bar(col_idx + 1, df[col_name][df['code'] == i], width=0.4, bottom=bottom,
                                        edgecolor='black', color='C' + str(i))
                color_list[col_name][labels_name[i]] = bar_colors.patches[-1].get_facecolor()
                bar_list[col_name][labels_name[i]] = df[col_name][df['code'] == i].values[0] + bottom
                #                 if i < 5:
                #                     ax.text(
                #                         1 + col_idx - 0.4 / 2 + 0.05,
                #                         bottom +50,
                #                         genes[i].split('B')[1],
                #                         size=7
                #                     )

                bottom += df.loc[genes[i], col_name]
        ax.legend(bbox_to_anchor=(1.05, 0), loc=3, borderaxespad=0, fontsize=5)
        gene_connect = pd.DataFrame(data[col_names].value_counts()).reset_index()
        gene_connect = gene_connect[gene_connect[col_names[0]] != gene_connect[col_names[1]]].reset_index(drop=True)
        bar_list_tmp = deepcopy(bar_list)
        for _, i in gene_connect.iloc[:maxshow, :].iterrows():
            connect_breakpoints = []
            height = i[0]
            connect_color = color_list[col_names[0]][i[col_names[0]]]
            for col_name in col_names:
                gene = i[col_name]
                top = bar_list_tmp[col_name][gene]
                connect_breakpoints.append((top - height, top))
                bar_list_tmp[col_name][gene] = top - height
            self._gapped_ribbons(
                connect_breakpoints,
                ax=ax,
                gapwidth=0.4,
                xstart=1.2,
                ribcol=connect_color,
            )
        ax.set_xticks(range(1, len(col_names) + 1))
        ax.set_xticklabels(['pre', 'post'])
        ax.set_yticks([])
        ax.set_title(tcr_sample)


#         plt.savefig('./test_img/' + self.name + '.png', bbox_inches='tight')


TCRDIV_METHOD = ['entropy', 'd50', 'gini', 'hill', 'dxx', 'gini-simp']


# https://en.wikipedia.org/wiki/Measurement_of_biodiversity
class TCRDiv:

    def __init__(self):
        pass

    def get_result(self, tcr_data, method='entropy', norm=False):
        if method not in TCRDIV_METHOD:
            raise AttributeError(f'Input right method{TCRDIV_METHOD}')
        if method == 'entropy':
            return self.entropy(tcr_data, norm)
        elif method == 'd50':
            return self.d50(tcr_data)
        elif method == 'gini':
            return self.gini(tcr_data)
        elif method == 'gini-simp':
            return self.gini_simpson(tcr_data)

    def get_plot(self, tcr_data, method='entropy', label_data=None, by=None, norm=False, show_L=True):
        if method not in TCRDIV_METHOD:
            raise AttributeError(f'Input right method{TCRDIV_METHOD}')
        if method == 'entropy':
            return self.plot_entropy(tcr_data, label_data, by, norm, show_L)
        elif method == 'd50':
            return self.plot_d50(tcr_data, label_data, by, show_L)

    def entropy(self, tcr_data, norm):
        entp_dict = {}
        for tcr, sample in zip(tcr_data[0], tcr_data[1]):
            entp_dict[sample] = tcr['frac'].apply(lambda x: -x * np.log2(x)).sum()
        if not norm:
            return pd.DataFrame.from_dict(entp_dict, orient='index', columns=['Entropy']).reset_index()
        else:
            entp_norm = pd.DataFrame.from_dict(entp_dict, orient='index', columns=['Entropy'])
            entp_norm['Entropy'] = entp_norm[['Entropy']].apply(lambda x: x / x.sum())
            return entp_norm.reset_index()

    def d50(self, tcr_data):
        prop = [np.cumsum(i['frac'].values) for i in tcr_data[0]]
        d50_df = pd.DataFrame([[np.abs(i - 50 / 100).argmin() + 1 for i in prop], tcr_data[1]],
                              index=['d50num', 'index']).T
        d50_df['d50num'] = d50_df['d50num'].astype('int')
        return d50_df[['index', 'd50num']]

    def gini(self, tcr_data):
        gini_dict = {}
        for tcr, sample in zip(tcr_data[0], tcr_data[1]):
            sorted_tcr = np.sort(tcr['frac'])
            n = len(tcr)
            cumx = np.cumsum(sorted_tcr, dtype=float)
            gini_dict[sample] = (n + 1 - 2 * np.sum(cumx) / cumx[-1]) / n
        return pd.DataFrame.from_dict(gini_dict, orient='index', columns=['Gini']).reset_index()

    def gini_simpson(self, tcr_data):
        gini_simp_dict = {}
        for tcr, sample in zip(tcr_data[0], tcr_data[1]):
            gini_simp_dict[sample] = 1 - sum([i * i for i in tcr['frac']])
        return pd.DataFrame.from_dict(gini_simp_dict, orient='index', columns=['Gini-Simpson']).reset_index()

    def hill_number(self, tcr_data):
        pass

    def plot_entropy(self, tcr_data, label_data, by, norm, show_L):
        entropy_data = self.entropy(tcr_data, norm)
        if entropy_data.shape[0] < 10:
            fig_s = 10
        else:
            fig_s = entropy_data.shape[0] / 3
        if label_data is None:
            base_plot = (ggplot(entropy_data, aes('index', 'Entropy'))
                         + geom_bar(aes(fill='index'), stat='identity', width=0.8, colour='black', size=.25)
                         + theme_bw() + theme(figure_size=(fig_s, 6.5), axis_text_x=element_text(angle=90, hjust=1)))
        else:
            # 获取输入元素label
            if by is not None and by not in label_data.columns:
                raise AttributeError(f"'DataFrame' object has no attribute '{by}'")
            if by is None:
                by = label_data.columns[2]

            entropy_data = pd.merge(entropy_data, label_data)
            base_plot = (ggplot(entropy_data, aes(x=by, y='Entropy', fill=by))
                         + geom_boxplot(show_legend=show_L) + geom_jitter(fill="black", shape=".", width=0, size=3,
                                                                          stroke=0.1)
                         + theme_bw() + theme(figure_size=(label_data[by].nunique() * 2, 6)))

        return base_plot + xlab('Sample') + ylab('Entropy')

    def plot_d50(self, tcr_data, label_data, by, show_L):
        d50_data = self.d50(tcr_data)
        if d50_data.shape[0] < 10:
            fig_s = 10
        else:
            fig_s = d50_data.shape[0] / 3
        if label_data is None:
            base_plot = (ggplot(d50_data, aes('index', 'd50num'))
                         + geom_bar(aes(fill='index'), stat='identity', width=0.8, colour='black', size=.25)
                         + theme_bw() + theme(figure_size=(fig_s, 6.5), axis_text_x=element_text(angle=90, hjust=1)))
        else:
            # 获取输入元素label
            if by is not None and by not in label_data.columns:
                raise AttributeError(f"'DataFrame' object has no attribute '{by}'")
            if by is None:
                by = label_data.columns[2]
            d50_data = pd.merge(d50_data, label_data)
            base_plot = (ggplot(d50_data, aes(x=by, y='d50num', fill=by))
                         + geom_boxplot(show_legend=show_L) + geom_jitter(fill="black", shape=".", width=0, size=3,
                                                                          stroke=0.1)
                         + theme_bw() + theme(figure_size=(label_data[by].nunique() * 2, 6)))

        return base_plot + xlab('Sample') + ylab('D50 Index')


TCROV_METHOD = ['heatmap', 'clustermap']


class TCROv:
    def __init__(self):
        pass

    def get_result(self, data, sep='_', unique_name=['vgene', 'jgene', 'cdr3aa']):
        unique_name = unique_name
        seq_list = [[] for i in range(len(data[0]))]
        for sampleId in range(len(data[0])):
            sep = sep
            seq_temp = data[0][sampleId][unique_name[0]]
            for col in unique_name[1:]:
                seq_temp = seq_temp + sep + data[0][sampleId][col]
            seq_list[sampleId] = set(seq_temp.values.tolist())
        overlap_index = []
        for sample_0 in range(len(seq_list)):
            for sample_1 in range(sample_0 + 1, len(seq_list)):
                overlap_index.append(
                    len(seq_list[sample_0] & seq_list[sample_1]) / len(seq_list[sample_0] | seq_list[sample_1]))
        overlap_index = squareform(overlap_index)
        np.fill_diagonal(overlap_index, 1)
        overlap_index = pd.DataFrame(overlap_index, index=data[1], columns=data[1])
        return overlap_index

    def get_plot(self, data, method='heatmap'):
        if method == 'heatmap':
            return sns.heatmap(self.get_result(data), cmap="RdBu_r")
        elif method == 'clustermap':
            return sns.clustermap(self.get_result(data), cmap="RdBu_r")
