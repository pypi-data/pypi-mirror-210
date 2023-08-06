import importlib
from typing import Union

import pandas as pd
from assertpy import assert_that

from deepdriver import logger
from deepdriver.sdk.chart.chart import Chart, TYPE_CONFUSION_MATRIX, TYPE_ROC_CURVE, TYPE_HISTOGRAM, TYPE_BAR
from deepdriver.sdk.data_types.image import Image
from deepdriver.sdk.data_types.table import Table
import numpy as np


def visualize(obj: Union[Chart, Table, Image]) -> None:
    assert_that(obj).is_not_none()

    def visualize_table(obj: Table):
        # from IPython.core.display import display, HTML
        # display(HTML(obj.data.dataframe._repr_html_()))

        plotly_path = "plotly.graph_objects"
        plotly_module = importlib.import_module(plotly_path)

        fig = plotly_module.Figure(
            data=[plotly_module.Table(
                header=dict(values=obj.data.columns),
                cells=dict(values=obj.data.dataframe.T))
            ],
        )
        fig.show()

    def visualize_image(obj: Image):
        # from IPython.core.display import display, HTML
        # display(HTML(obj.data.dataframe._repr_html_()))

        plotly_path = "plotly.express"
        plotly_module = importlib.import_module(plotly_path)

        fig = plotly_module.imshow(
            np.array(obj.data)
        )
        # show bounding boxes and  box caption ( annotations )
        if obj.boxes:
            if 'box_data' not in obj.boxes.to_dict():
                return

            for box in obj.boxes.to_dict()['box_data']:
                box: dict = box
                if "position" in box:
                    fig.add_shape(
                        type='rect',
                        x0=box["position"]["minX"], x1=box["position"]["maxX"], y0=box["position"]["minY"],
                        y1=box["position"]["maxY"],
                        xref='x', yref='y',
                        line_color='blue'
                    )

                if "caption" in box:
                    fig.add_annotation(
                        x=box["position"]["minX"],
                        xanchor='left',
                        y=box["position"]["minY"] - 12,
                        yanchor='top',
                        text=box["caption"],
                        showarrow=False,
                        font_size=16, font_color='white', bgcolor='black', )

        # show image caption
        if obj.caption:
            fig.update_layout(
                title={
                    'text': f'<span style="font-size: 22px;">{obj.caption}</span>',
                    'x': 0.5,
                    'y':0.02,
                },

            )
        fig.show()

    def visualize_chart_common(obj: Chart):
        # line, scatter 차트
        plotly_path = "plotly.express"
        plotly_module = importlib.import_module(plotly_path)
        plotly_chart_func = getattr(plotly_module, obj.chart_type)

        fig = plotly_chart_func(
            x=obj.data.dataframe[obj.data_fields["x"]],
            y=obj.data.dataframe[obj.data_fields["y"]],
            labels=obj.data_fields,
            title=obj.label_fields["title"],
        )
        fig.show()

    def visualize_chart_bar(obj: Chart):
        # bar 차트
        plotly_path = "plotly.express"
        plotly_module = importlib.import_module(plotly_path)
        plotly_chart_func = getattr(plotly_module, obj.chart_type)

        fig = plotly_chart_func(
            obj.data.dataframe,
            x=obj.data_fields["x"],
            y=obj.data_fields["y"],
            labels=obj.data_fields,
            title=obj.label_fields["title"],
        )
        fig.show()

    def visualize_chart_histogram(obj: Chart):
        # historgram
        plotly_path = "plotly.express"
        plotly_module = importlib.import_module(plotly_path)
        plotly_chart_func = getattr(plotly_module, obj.chart_type)

        if obj.data_fields["y"]:
            fig = plotly_chart_func(
                obj.data.dataframe,
                x=obj.data_fields["x"],
                y=obj.data_fields["y"],
                labels=obj.data_fields,
                title=obj.label_fields["title"],
            )
            fig.show()
        else:
            fig = plotly_chart_func(
                obj.data.dataframe,
                x=obj.data_fields["x"],
                labels=obj.data_fields,
                title=obj.label_fields["title"],
            )
            fig.show()

    def visualize_confusion_matrix(obj: Chart):
        # dataframe 에서 x, y, z 값 추출
        actual = obj.data.dataframe['Actual']
        predicted = obj.data.dataframe['Predicted']
        n_redictions = obj.data.dataframe['nPredictions']
        cross_tab_df = pd.crosstab(index=actual, columns=predicted, values=n_redictions, aggfunc=sum)
        logger.debug(f"cross_tab_df : \n{cross_tab_df}")
        """ cross_tab_df
        Predicted  cat  dog  horse
        Actual                    
        cat        5.0  2.0    0.0
        dog        0.0  4.0    1.0
        horse      1.0  0.0    3.0
        """
        labels, z = [], []
        for item in cross_tab_df.transpose().iteritems():
            # item : ('cat', 'list[]')
            labels.append(item[0])
            z.append(list(item[1]))

        # 그래프 그리기
        plotly_path = "plotly.graph_objects"
        plotly_module = importlib.import_module(plotly_path)
        data = plotly_module.Heatmap(z=z, x=labels, y=labels)
        annotations = []
        for i, row in enumerate(z):
            for j, value in enumerate(row):
                annotations.append(
                    {
                        "x": labels[i],
                        "y": labels[j],
                        # "font": {"color": "white"},
                        "text": z[j][i],
                        "xref": "x",
                        "yref": "y",
                        "showarrow": False
                    }
                )
        layout = {
            "title": obj.label_fields["title"],
            "xaxis": {"title": "Predicted"},
            "yaxis": {"title": "Actual"},
            "annotations": annotations
        }
        fig = plotly_module.Figure(data=data, layout=layout)
        fig.show()

    def visualize_roc_curve(obj: Chart):
        """
           class  fpr    tpr
        0   cat  0.0  0.000
        1   cat  0.0  0.500
        2   cat  0.0  1.000
        3   cat  1.0  1.000
        4   dog  0.0  0.000
        5   dog  0.0  0.333
        6   dog  0.0  1.000
        7   dog  1.0  1.000
        """
        plotly_path = "plotly.graph_objects"
        plotly_module = importlib.import_module(plotly_path)

        fig = plotly_module.Figure()
        fig.add_shape(
            type='line', line=dict(dash='dash'),
            x0=0, x1=1, y0=0, y1=1
        )

        df = obj.data.dataframe
        classes = df['class'].unique()
        for class_ in classes:
            fpr = list(df.loc[df['class'] == class_]['fpr'])
            tpr = list(df.loc[df['class'] == class_]['tpr'])
            logger.debug(f"class_:{class_}/ fpr:{fpr} / tpr:{tpr}")
            fig.add_trace(plotly_module.Scatter(x=fpr, y=tpr, name=class_, mode='lines'))

        fig.update_layout(
            title=obj.label_fields["title"],
            xaxis_title='False Positive Rate',
            yaxis_title='True Positive Rate',
            yaxis=dict(scaleanchor="x", scaleratio=1),
            xaxis=dict(constrain='domain'),
        )
        fig.show()

    if isinstance(obj, Chart):
        if obj.chart_type == TYPE_CONFUSION_MATRIX:
            visualize_confusion_matrix(obj)
        elif obj.chart_type == TYPE_ROC_CURVE:
            visualize_roc_curve(obj)
        elif obj.chart_type == TYPE_HISTOGRAM:
            visualize_chart_histogram(obj)
        elif obj.chart_type == TYPE_BAR:
            visualize_chart_bar(obj)
        else:
            visualize_chart_common(obj)
    elif isinstance(obj, Table):
        visualize_table(obj)
    elif isinstance(obj, Image):
        visualize_image(obj)
