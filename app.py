import streamlit as st
import pandas as pd
import pydeck as pdk
import csv

class ColumnMap:

    # マップのスタイルを選択
    def mapstyle():

        object = st.sidebar.selectbox(
            "マップ:",
            options=["dark", "light", "satellite", "road"],
            format_func=str.capitalize,
        )
        return object
    
    # 指標を選択
    def indicator():
        object = st.sidebar.selectbox(
            "指標:",
            options=["合計特殊出生率", "財政力指数", "平均所得"],
            format_func=str.capitalize,
        )
        return object
    
    # 係数を分岐
    def branch_coefficient(dataframe, object): 
        df, indicator = dataframe, object
    
        if indicator == "合計特殊出生率":
            df['float'] = df[indicator].apply(lambda x: x **7 ) #
        elif indicator == "財政力指数":
            df['float'] = df[indicator].apply(lambda x: (x+1) **4) #
        elif indicator == "平均所得":
            min_value = df[indicator].min()
            df['float'] = df[indicator].apply(lambda x: (x-min_value)/100000) #
        elif indicator == "経常収支比率":
            min_value = df[indicator].min()
            df['float'] = df[indicator].apply(lambda x: x-min_value) #
        elif indicator == "将来負担比率":
            df[indicator] = df[indicator].apply(lambda x: 0 if '-' in str(x) else x)
            df[indicator] = df[indicator].apply(lambda x: float(x.replace('-', '0')) if isinstance(x, str) else x)
            df['float'] = df[indicator].apply(lambda x: x) #

        elif indicator == "ラスパイレス指数":
            min_value = df[indicator].min()
            
            df['float'] = df[indicator].apply(lambda x: x-min_value) #

        return df['float'] 

    def branch_color(dataframe, object):

        # SettingWithCopyWarningを回避するため
        df = dataframe.copy() 
        indicator = object
    
        lis = [[0,255,255], [0,204,255], [0,102,204], [0, 0, 255], [0, 0, 129], [255, 0, 0]]
        lis = lis if indicator not in ['将来負担比率'] else lis[::-1]
        # カラーマッピング関数
        def color_scale(max_value, min_value, value):
            step = (max_value - min_value) / 6

            if value == 0:
                return [0, 0, 0] # 黒
            elif value >= max_value - 1 * step:
                return lis[0]# 
            elif value >= max_value - 2 * step:
                return lis[1]
            elif value >= max_value - 3 * step:
                return lis[2]
            elif value >= max_value - 4 * step:
                return lis[3] # 青
            elif value >= max_value - 5 * step:
                return lis[4] # ダークブルー
            else:
                return lis[5] # 赤
               
        max_value = df[indicator].max()

        # 0を排除
        df_ = df[df[indicator] != 0]
        min_value = df_[indicator].min()

        df['color'] = df[indicator].apply(lambda x: color_scale(max_value, min_value, x))
        return df['color']

    @staticmethod
    def drawing(dataframe):
        df = dataframe
        indicator = f'{ColumnMap.indicator()}'  # 選択された指標
        
        df['float'] = ColumnMap.branch_coefficient(df, indicator) 
        
        view = pdk.ViewState(
            longitude=139.6017,
            latitude=35.5895,
            zoom=8,
            pitch=40,
        )
        
        df['color'] = ColumnMap.branch_color(df, indicator)

        # レイヤーの設定
        layer = pdk.Layer(
            "ColumnLayer",
            data=df,
            get_position="[longitude, latitude]",
            radius=1000,
            elevation_scale=300,
            #elevation_range=[0, df['float'].max()*100],
            get_elevation='float',
            get_fill_color='color',
            coverage=1.9, # ヘクサゴンの重なり具合
            auto_highlight=True, # ホバーした円柱をハイライトする
            pickable=True, # ツールチップを表示したいのでtrueにする
            extruded=True,
        )

        # レイアウトの設定
        r = pdk.Deck(
            map_provider="mapbox",
            #map_style=pdk.map_styles.CARTO_LIGHT,
            map_style=f"{ColumnMap.mapstyle()}",  # 'light', 'dark', 'satellite', 'road'
            # map_style=pdk.map_styles.SATELLITE,
            layers=[layer],
            initial_view_state=view,
            tooltip={
                "html": "<b>{都道府県}  {市区町村}</b><br><b>合計特殊出生率:</b>{合計特殊出生率}<br><b>財政力指数:</b>{財政力指数}<br><b>平均所得:</b>{平均所得}<br>", 
                "style": {"backgroundColor": "steelblue", "color": "white"}
            } 
        )

        # Streamlitに表示
        st.pydeck_chart(r)

    @st.cache_data
    def load_data():
        df = pd.read_csv('./data/municipalities.csv', sep=",", encoding='utf-8') # tokyo.csv
        return df
        
    def main():
        st.title("東京都の合計特殊出生率・財政力指数・平均所得")
        
        df = ColumnMap.load_data()
       

        ColumnMap.drawing(df)

        st.markdown("""

            ※本グラフは値を視覚的に強調するため、係数を用いた値で描画しています。

        """)

        with st.expander("参照データ"):
            dic = {
                "人口動態統計特殊報告": '平成30年～令和４年人口動態保健所・市区町村別統計の概況',
                "年": "2020年（令和2年）",
                "※": "楢葉町、富岡町、川内村、大熊町、双葉町、浪江町、葛尾村、飯舘村、球磨村のデータなし",
                "URL": "https://www.mhlw.go.jp/toukei/saikin/hw/jinkou/other/hoken24/index.html"
            }
            df_info = pd.DataFrame(dic, index=[""]).T
            st.table(df_info)

            dic = {
                "作成": '総務省',
                "名称": '令和4年度地方公共団体の主要財政指標一覧',
                "": "全市町村の主要財政指標",
                "年": "2020年（令和2年）",
                "URL": "https://www.soumu.go.jp/iken/zaisei/R04_chiho.html"
            }
            df_info = pd.DataFrame(dic, index=[""]).T
            st.table(df_info)
            """
            １．財政力指数
            　表最下段の各平均値は、単純平均であり、東京都特別区、一部事務組合及び広域連合を含まない。
            """
        
            dic = {
                "作成": '総務省',
                "名称": '市町村税課税状況等の調',
                "※": "課税対象所得を所得割の納税義務者数で割って平均所得は求められている",
                "年": "2020年（令和2年）",
                "URL": "https://www.soumu.go.jp/main_sosiki/jichi_zeisei/czaisei/czaisei_seido/ichiran09.html"
            }
            df_info = pd.DataFrame(dic, index=[""]).T
            st.table(df_info)  
            df_ =df.drop(df.columns[[1,2,4]], axis=1)
            st.dataframe(df_)#
        
        st.subheader("凡例")
        st.markdown("""
            <ul style="list-style-type:none;"></li>
            <li><span style="color: #00FFFF;">■</span>最も高い</li>    
            <li><span style="color: #00CCFF;">■</span>高い</li> 
            <li><span style="color: #0066CC;">■</span>中程度</li>
            <li><span style="color: #0000FF;">■</span>やや低い</li>
            <li><span style="color: #000080;">■</span>低い</li>       
            <li><span style="color: red;">■</span>最も低い</li>    
            </ul>

        """, unsafe_allow_html=True)
class MatrixSorting:
    # CSVファイルを読み込む関数
    def read_csv_as_dict(filename):
        data = []
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        return data

    # 並び替える関数
    def sort_by_city_names(data, city_names):
        # 市町村名をキーにした辞書を作成
        city_dict = {row['市町村名']: row for row in data}
        # 指定された順序に並び替え
        sorted_data = [city_dict[city] for city in city_names if city in city_dict]
        return sorted_data
    
    def main():
        
        df = ColumnMap.load_data()
        # 並べ替えたい市町村名のリスト
        city_names =  list(df['市区町村']) 

        # ファイル名
        input_filename = './data/市区町村別所得.csv'
        output_filename = 'sorted_data.csv'

        # CSVファイルを辞書として読み込み
        data = MatrixSorting.read_csv_as_dict(input_filename)

        # 並べ替えたい市町村名のリスト
        city_names = list(df['市区町村']) 

        # 並べ替え
        sorted_data = MatrixSorting.sort_by_city_names(data, city_names)

        # 結果をCSVファイルに出力
        with open(output_filename, mode='w', encoding='utf-8', newline='') as file:
            fieldnames = ['都道府県名', '市町村名', '平均所得']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sorted_data)

        (f"データは {output_filename} に出力されました。")

if __name__ == '__main__':
    ColumnMap.main()



