# Excel 操作速查 (openpyxl)

## 基础操作

```python
import openpyxl

# === 读 ===
wb = openpyxl.load_workbook('path/to/file.xlsx')

# 获取所有 sheet 名
print(wb.sheetnames)

# 选 sheet
ws = wb.active          # 当前活动的 sheet
ws = wb['邀约追踪']      # 按名称选

# 读全部行（跳过表头）
for row in ws.iter_rows(min_row=2, values_only=True):
    name, fans, city = row[0], row[1], row[2]

# 读指定列
col_a = [cell.value for cell in ws['A']]

# === 写 ===
wb = openpyxl.Workbook()
ws = wb.active
ws.title = '邀约追踪'

# 写表头
ws.append(['Name', 'Fans', 'City', 'Status'])

# 写数据行
ws.append(['达人A', 50000, '上海', 'OK'])

# 保存
wb.save('output.xlsx')
```

## 常用技巧

```python
# 追加到已有表末尾
ws.append(['new', 'row', 'data'])

# 获取当前行数
max_row = ws.max_row

# 在最后一行后面追加
ws.cell(row=ws.max_row+1, column=1, value='新数据')

# 遍历所有行（含表头）
for row in ws.iter_rows(values_only=True):
    print(row)

# 只读模式（大文件更快）
wb = openpyxl.load_workbook('file.xlsx', read_only=True)

# 自动筛选
ws.auto_filter.ref = 'A1:J1'

# 冻结首行
ws.freeze_panes = 'A2'
```

## 样式速查

```python
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

font = Font(name='微软雅黑', bold=True, size=11, color='FFFFFF')
fill = PatternFill(start_color='FF6B35', end_color='FF6B35', fill_type='solid')
align = Alignment(horizontal='center', vertical='center')
border = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)

cell.font = font
cell.fill = fill
cell.alignment = align
cell.border = border

# 列宽
ws.column_dimensions['A'].width = 20
ws.column_dimensions['B'].width = 15
```

## 邀约追踪表列定义

| 列 | 标题 | 示例值 |
|----|------|--------|
| A | 序号 | 1 |
| B | 达人昵称 | 苏苏爱吃鱼 |
| C | 粉丝数 | 265000 |
| D | 城市 | 杭州 |
| E | 内容标签 | 女装, 穿搭 |
| F | 微信 | LLL928113 |
| G | 手机号 | 13065813130 |
| H | 邀约日期 | 2026-07-15 |
| I | 邀约ID | 22064022 |
| J | 状态 | OK / FAIL:xxx / SKIP |
| K | 邀约留言 | 您好！我们是... |
| L | 备注 | 手动补充 |
