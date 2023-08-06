"""The ability to render a bar chart quickly and easily from data is a key skill
for any data scientist working in Python"""

# From https://www.shanelynn.ie/bar-plots-in-python-using-pandas-dataframes/

# Style Reference: https://matplotlib.org/stable/gallery/style_sheets/style_sheets_reference.html
# matplotlib.style.use('fivethirtyeight')
import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def bar_plot(data, x, y, hue=None, y_lim=None, title=None, legend_outside=False, png_path='Project_Test.png'):
    
    assert isinstance(data, pd.DataFrame), "Input data is expected to be pandas.DataFrame, not {}".format(type(data))
    
    sns.set(style="ticks", palette="pastel")
    if hue is None:
        ax = sns.barplot(x=x, y=y, data=data)
    else:
        ax = sns.barplot(x=x, y=y, hue=hue, data=data)
    for p in ax.containers:
        ax.bar_label(p, label_type='center', labels=[f'{val:.2f}' for val in p.datavalues], fontsize=12)
    
    if y_lim is not None:
        plt.ylim(y_lim)    
    
    if title is not None:
        plt.title(title)

    if legend_outside:
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
    
    
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
    plt.savefig(png_path, dpi=600, bbox_inches='tight')
    plt.close()        

def box_plot(data, x, y, hue=None, y_lim=None, title=None, showmeans=False, legend_outside=False, threshold=None, png_path='Project_Test.png'):
    
    assert isinstance(data, pd.DataFrame), "Input data is expected to be pandas.DataFrame, not {}".format(type(data))
    
    sns.set(style="ticks", palette="pastel")
    
    if hue is None:
        if showmeans:
            sns.boxplot(x=x, y=y, data=data, showmeans=True, meanprops={"marker":"o"})
        else:
            sns.boxplot(x=x, y=y, data=data)            
    else:
        
        if showmeans:
            sns.boxplot(x=x, y=y, hue=hue, data=data, showmeans=True, meanprops={"marker":"o"})
        else:
            sns.boxplot(x=x, y=y, hue=hue, data=data)    
    
    if threshold is not None:
        plt.axhline(y=threshold, color='r', linestyle='-')
    
    if y_lim is not None:
        plt.ylim(y_lim)    
        
    if title is not None:
        plt.title(title)
    
    if legend_outside:
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
    
    
    sns.despine(offset=0, trim=True)
    plt.savefig(png_path, dpi=600, bbox_inches='tight')
    plt.close()
    
if __name__ ==  '__main__':

    pass
            
            