import pandas as pd
import altair as alt

def test():
    # 1. Donut Chart Test
    chart_data_donut = pd.DataFrame({
        "Category": ["SaaS", "Security", "Hardware", "Analytics"],
        "Revenue": [120000.0, 80000.0, 150000.0, 50000.0]
    })
    x_col = chart_data_donut.columns[0]
    y_col = chart_data_donut.columns[1]
    
    donut_chart = alt.Chart(chart_data_donut).mark_arc(
        innerRadius=70, 
        stroke="#0b0f19", 
        strokeWidth=2
    ).encode(
        theta=alt.Theta(field=y_col, type="quantitative"),
        color=alt.Color(
            field=x_col, 
            type="nominal",
            scale=alt.Scale(scheme="tableau20")
        ),
        tooltip=[x_col, y_col]
    ).properties(
        height=350
    ).configure_legend(
        labelColor="#e2e8f0",
        titleColor="#e2e8f0"
    ).configure_view(
        strokeWidth=0
    )
    
    # 2. Line Chart Test
    chart_data_line = pd.DataFrame({
        "Month": ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05"],
        "Revenue": [140000.0, 155000.0, 160000.0, 145000.0, 125000.0]
    })
    x = "Month"
    y = "Revenue"
    line = alt.Chart(chart_data_line).mark_line(
        interpolate="monotone",
        color="#3b82f6",
        strokeWidth=3
    ).encode(
        x=alt.X(field=x, type="nominal", sort=None, title=x),
        y=alt.Y(field=y, type="quantitative", title=y),
        tooltip=[x, alt.Tooltip(field=y, format="$,.2f")]
    )
    
    points = alt.Chart(chart_data_line).mark_point(
        color="#60a5fa",
        size=60,
        filled=True
    ).encode(
        x=alt.X(field=x, type="nominal", sort=None),
        y=alt.Y(field=y, type="quantitative"),
        tooltip=[x, alt.Tooltip(field=y, format="$,.2f")]
    )
    
    full_line_chart = (line + points).properties(
        height=350
    ).configure_axis(
        labelColor="#94a3b8",
        titleColor="#e2e8f0",
        gridColor="#1e293b"
    ).configure_view(
        strokeWidth=0
    )
    
    # 3. Bar Chart Test
    chart_data_bar = pd.DataFrame({
        "Region": ["North", "South", "East", "West"],
        "Revenue": [180000.0, 220000.0, 110000.0, 195000.0]
    })
    x_bar = "Region"
    y_bar = "Revenue"
    bar = alt.Chart(chart_data_bar).mark_bar(
        cornerRadiusTopLeft=6,
        cornerRadiusTopRight=6,
        color="#3b82f6"
    ).encode(
        x=alt.X(field=x_bar, type="nominal", sort="-y", title=x_bar),
        y=alt.Y(field=y_bar, type="quantitative", title=y_bar),
        color=alt.Color(
            field=x_bar,
            type="nominal",
            scale=alt.Scale(scheme="tableau10"),
            legend=None
        ),
        tooltip=[x_bar, alt.Tooltip(field=y_bar, format="$,.2f")]
    ).properties(
        height=350
    ).configure_axis(
        labelColor="#94a3b8",
        titleColor="#e2e8f0",
        gridColor="#1e293b"
    ).configure_view(
        strokeWidth=0
    )

    print("All Altair charts compiled successfully!")

if __name__ == "__main__":
    test()
