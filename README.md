### NCAA Bracket Builder
##### Tweak your picks to create real brackets to beat your friends

This is a quick dashboard I threw together to interact with my predictions from the [Google Cloud & NCAA® ML Competition 2020-NCAAM](https://www.kaggle.com/c/google-cloud-ncaa-march-madness-2020-division-1-mens-tournament) competition on Kaggle. You will need to drop some of the Kaggle formatted data and your submission file into the inputs folder and then run the dashboard using [Streamlit](https://www.streamlit.io/). To start, put the necessary data in the input folder and rename or edit the file paths/names at the top of thes streamlit code. Finally, type:

'''
streamlit run NCAA_BracketBuilder_Sreamlit.py
'''
  
Dependencies:
* [Streamlit](https://github.com/streamlit/streamlit)
* [Graphvis](https://pypi.org/project/graphviz/) - (Python implementation only - standalone not needed)
* [Pandas](https://github.com/pandas-dev)
* [Numpy](https://github.com/numpy/numpy)