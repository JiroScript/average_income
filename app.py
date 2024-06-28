import streamlit as st
import pandas as pd
import pydeck as pdk
class Population:    
    # データの読み込み
    @st.cache_data
    def load_data():
        df = pd.read_csv('./data/d5.csv') #, nrows= 10
        return df
    
    def create_df(generation, gender):
                    
        # 世代ごとに分岐
        def branch_out_by_generation(generation, gender, dic):

            # 性別ごとに要素を抽出
            def extract_by_gender(lis, gender):
                if gender == "男女":
                    return lis
                elif gender == "男性":
                    return [ e for e in lis if "男" in e]
                elif gender == "女性":
                    return [ e for e in lis if "女" in e]

            if generation == '年少':
                return extract_by_gender(dic["年少"], gender)

            elif generation == '若年':
                return extract_by_gender(dic["若年"], gender)

            elif generation == '生産年齢':
                return extract_by_gender(dic["生産年齢"], gender)
                
            elif generation == '高齢':
                return extract_by_gender(dic["高齢"], gender)

            else:
                return extract_by_gender(dic["全世代"], gender)
            
        df = Population.load_data()
        dic = {"全世代": ["総数男", "総数女"], 
             "年少":['０～４歳男', '５～９歳男', '１０～１４歳男', '０～４歳女', '５～９歳女', '１０～１４歳女'], 
             "若年":["１５～１９歳男",	"２０～２４歳男",	"２５～２９歳男",	"３０～３４歳男", "１５～１９歳女",	"２０～２４歳女",	"２５～２９歳女",	"３０～３４歳女"], 
             "生産年齢":["１５～１９歳男",	"２０～２４歳男",	"２５～２９歳男",	"３０～３４歳男",	"３５～３９歳男",	"４０～４４歳男",	"４５～４９歳男",	"５０～５４歳男",	"５５～５９歳男",	"６０～６４歳男", "１５～１９歳女",	"２０～２４歳女",	"２５～２９歳女",	"３０～３４歳女",	"３５～３９歳女",	"４０～４４歳女",	"４５～４９歳女",	"５０～５４歳女",	"５５～５９歳女",	"６０～６４歳女"], 
             "高齢":["６５～６９歳男",	"７０～７４歳男",	"７５～７９歳男",	"８０～８４歳男",	"８５～８９歳男",	"９０～９４歳男",	"９５～９９歳男",	"１００歳以上男","６５～６９歳女",	"７０～７４歳女",	"７５～７９歳女",	"８０～８４歳女",	"８５～８９歳女",	"９０～９４歳女",	"９５～９９歳女",	"１００歳以上女"]}
       
        lis = branch_out_by_generation(generation, gender, dic)

        df['人口'] = df[dic["全世代"]].sum(axis=1)

        # 世代別の人口を合算
        generation_gender = generation + gender 
        df[generation_gender] = df[lis].sum(axis=1)
               
        # 人口比を算出
        df["%"] = round(((df[generation_gender]) / df[generation_gender].sum()) * 100, 3)

        # 結果を表示する
        return df
    
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
            options=["人口", "合計特殊出生率", "財政力指数", "平均所得"],
            format_func=str.capitalize,
        )
        return object
    
    def generations():
        object = st.sidebar.selectbox(
            "世代:",
            options=["全世代", "年少", "若年", "生産年齢", "高齢"],
            format_func=str.capitalize,
        )
        return object
    
    def gender():
        object = st.sidebar.selectbox(
            "性別:",
            options=["男女", "男性", "女性"],
            format_func=str.capitalize,
        )
        return object

    # 係数を分岐
    def branch_coefficient(dataframe, object, generation, gender): 
        df, indicator = dataframe, object
        if indicator == "人口":
            d_ = Population.create_df(generation, gender)

            # dataframeを結合
            df = pd.merge(df, d_)
            df['float'] = df["%"].apply(lambda x: x * 100 ) #

        elif indicator == "合計特殊出生率":
            df['float'] = df[indicator].apply(lambda x: x **7 ) #

        elif indicator == "財政力指数":
            df['float'] = df[indicator].apply(lambda x: (x+1) **4) #

        elif indicator == "平均所得":
            min_value = df[indicator].min()
            df['float'] = df[indicator].apply(lambda x: (x-min_value)/100000) #

        return df, df['float'] 

    def branch_color(dataframe, object, generation, gender):

        # SettingWithCopyWarningを回避するため
        df = dataframe.copy() 
        indicator = object
    
        lis = [ [0, 255, 255], [3, 120, 255], [26, 128, 249], [22, 107, 237], [18, 86, 216], [13, 64, 194], [9, 43, 172], [0,0,255], [0,0,205], [0, 0, 129]]
        
        # カラーマッピング関数 rankの値によって色を決定
        def rank_based_color_scale(value, dataframe, indicator, generation, gender):
            df = dataframe

            # rankの値から同じ行の他の列の値を取得する
            indicator_value = df.loc[df['rank'] == value, indicator].values[0]  
            #st.write(value, indicator_value)
            step = len(df["rank"]) / 9

            if indicator_value == 0:
                return [0, 0, 0]

            elif value <= 10:
                return lis[0] # 
            
            elif value <= 1 * step:
                return lis[1] # 
            
            elif value <= 2 * step:
                return lis[2]
            
            elif value <= 3 * step:
                return lis[3]
            
            elif value <= 4 * step:
                return lis[4] # 青
            
            elif value <= 5 * step:
                return lis[5] # 
            
            elif value <= 6 * step:
                return lis[6] # 
            
            elif value <= 7 * step:
                return lis[7] # 
            
            elif value <= 8 * step:
                return lis[8] # 
            
            else:
                return lis[9] # 赤
        
        # 人口の総数を取得
        if indicator == '人口':
            df['rank'] = df[generation + gender].rank(method='min', ascending=False)
        else:
            df['rank'] = df[indicator].rank(method='min', ascending=False)
        
        df['color'] = df['rank'].apply(lambda x: rank_based_color_scale(x, df, indicator, generation, gender))
        # カラーコードのリストと比較するために、リストをタプルに変換
        df['color'] = df['color'].apply(tuple)
        count_cyan = (df['color'] == (0, 0, 129)).sum()
        st.write(count_cyan)
        count_cyan = (df['color'] == (255, 0, 0)).sum()
        st.write(count_cyan)
        

        return df, df['color']

    @staticmethod
    def drawing(dataframe):
        df = dataframe
        indicator = f'{ColumnMap.indicator()}'  # 選択された指標

        if indicator == "人口":
            generation, gender = f'{ColumnMap.generations()}', f'{ColumnMap.gender()}'
            generation_gender = generation + gender
        else:
            generation, gender = None, None

        df, df['float'] = ColumnMap.branch_coefficient(df, indicator, generation, gender) 
        
        view = pdk.ViewState(
            longitude=139.6017,
            latitude=35.5895,
            zoom=8,
            pitch=40,
        )
        
        df, df['color'] = ColumnMap.branch_color(df, indicator, generation, gender)

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

            map_style=f"{ColumnMap.mapstyle()}",  # 'light', 'dark', 'satellite', 'road'

            layers=[layer],
            initial_view_state=view,
            tooltip={
                "html": f"<b>{{都道府県}}  {{市区町村}}</b><br><b>人口:</b>{{人口}}<br><b>世代別人口</b><small>（{generation}:{gender}）</small>:&nbsp;{{{generation_gender}}}&nbsp;&nbsp;{{%}}<b> %</b><br><b>合計特殊出生率:</b>{{合計特殊出生率}}<br><b>財政力指数:</b>{{財政力指数}}<br><b>平均所得:</b>{{平均所得}}<br>", 
                "style": {"backgroundColor": "steelblue", "color": "white"}
            } if indicator == "人口" else {
                "html": f"<b>{{都道府県}}  {{市区町村}}</b><br><br><b>合計特殊出生率:</b>{{合計特殊出生率}}<br><b>財政力指数:</b>{{財政力指数}}<br><b>平均所得:</b>{{平均所得}}<br>", 
                "style": {"backgroundColor": "steelblue", "color": "white"}
            }
        )
        # Streamlitに表示
        st.pydeck_chart(r)
        if indicator in ["合計特殊出生率", "財政力指数"]:
            st.markdown("""
                ※本グラフは値を視覚的に強調するため、係数を用いた値で描画しています。
            """)

    @st.cache_data
    def load_data():
        df = pd.read_csv('./data/municipalities.csv', sep=",", encoding='utf-8') # tokyo.csv
        return df
        
    def main():
        ("東京都の合計特殊出生率・財政力指数・平均所得")
        
        df = ColumnMap.load_data()

        ColumnMap.drawing(df)

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
            <li><span style="color: #0066CC;">■</span>高い</li> 
            <li><span style="color: #001eff;">■</span>中程度</li>
            <li><span style="color: blue;">■</span>低い</li>
            <li><span style="color: #000080;">■</span>最も低い</li>       
            <li><span style="color: black;">■</span>数値なし</li>    
            </ul>

        """, unsafe_allow_html=True)

if __name__ == '__main__':
    ColumnMap.main()



