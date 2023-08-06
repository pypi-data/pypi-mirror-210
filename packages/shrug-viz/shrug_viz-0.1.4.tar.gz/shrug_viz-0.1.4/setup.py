#!/usr/bin/env python
# coding: utf-8

# In[8]:


from setuptools import setup,find_packages


# In[1]:


setup(
    name='shrug_viz',
    version='0.1.4',
    author='Kashmira L, Maithili K, Vibhuti D, Pradnya K',
    author_email='kashmira.lodha@cumminscollege.in, pradnya.kanale@cumminscollege.in, vibhuti.dhande@cumminscollege.in, maithili.karlekar@cumminscollege.in',
    description='Choropleth visualization for SHRUG data platform (SAMOSA version)',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'plotly',
        'numpy',
        'jellyfish',
        'matplotlib',
        'geopandas',
        'pkg_resources'
    ],
    include_package_data=True,
    package_data={'': ['data/*']},
)


# In[ ]:




