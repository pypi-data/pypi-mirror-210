


# # %%
# import pandas as pd
# error_df = pd.read_csv('error_df.csv')

# # %%
# error_df = error_df.head(1000)
# error_df.to_csv('small.csv')

# df_1 = error_df[['result','Unnamed: 0']]

# df_2 = error_df[['truth','image_path']]

# df_1.to_csv('df_1.csv')

# df_2.to_csv('df_2.csv')

# # %%
# from hg_test_quick_object_oriented import download_dict,homoglyph_distance,homoglyph_merge
# import pandas as pd

# #cluster_dict = download_dict('ko')#specify and load the dicts
# download_dict('ko')
# homoglyph_distance('我','我是')

#  %%
## The merge can be run with this - just no multiprocessing currently...
'''
Questions and to dos: deal with no matches
This is return top 10 and the distance
'''
from hg_test_quick_object_oriented import download_dict,homoglyph_distance,homoglyph_merge
import pandas as pd

df_1 = pd.read_csv('df_1.csv')
df_2 = pd.read_csv('df_2.csv')

df_1 = df_1.head(1000)
df_2 = df_2.head(1000)

## Dataframe merge

## No need to download dicts again...
dataframe_merged = homoglyph_merge('ko',df_1,df_2,'result','truth',parallel=True)
dataframe_merged.to_csv('merged_4.csv')
# %%
'''
Parameters:
lang
dataframe 1
dataframe 2
key on dataframe 1
key on dataframe 2
'''
## Also need to pass in dataframe later on
dataframe_merged.to_csv('merged.csv')
# %%
## The distance calculation
#!pip3 install -i https://test.pypi.org/simple/ homoglyphs-testpypi==0.0.1



cluster_dict = download_dict('ko')
homoglyph_distance('我','我是',cluster_dict)


# %%

df_1 = pd.read_csv('df_1.csv')
df_2 = pd.read_csv('df_2.csv')

# %%
import pandas as pd
from hg_functions import homoglyph_merge, homoglyph_distance
df_1 = pd.DataFrame(list(['苏萃乡','办雄','虐格给','雪拉普岗']),columns=['ocred_text'])
df_2 = pd.DataFrame(list(['雪拉普岗日','小苏莽乡','协雄','唐格给']),columns=['truth_text'])

## Dataframe merge
#dataframe_merged = homoglyph_merge('zhs',df_1,df_2,'ocred_text','truth_text',parallel=True)

dataframe_merged = homoglyph_merge('zhs',df_1,df_2,'ocred_text','truth_text',homo_lambda=2, insertion=1, deletion=1,parallel=True,num_workers=4)



homoglyph_distance('我目','我日')
'''
Parameters:
lang
dataframe 1
dataframe 2
key on dataframe 1
key on dataframe 2
'''
## Also need to pass in dataframe later on
dataframe_merged.to_csv('merged_5.csv')

# %%
'''
Implement the dataframe...and download dictionary
'''
print(homoglyph_distance('我目','我日'))


# %%
