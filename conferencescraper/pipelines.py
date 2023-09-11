import xlsxwriter


class ConferencescraperPipeline:

    def __init__(self):
        self.workbook = None
        self.worksheet = None
        self.current_row = 3

    def process_item(self, item, spider):
        name_and_affiliation = item.get('name_and_affiliation')
        location = item.get('location')
        session_name = item.get('session_name')
        title = item.get('title')
        text = item.get('text')

        body = self.workbook.add_format({
            'text_wrap': True,
            'font_size': 10
        })

        for name in name_and_affiliation:
            self.worksheet.write(self.current_row, 0, name, body)
            self.worksheet.write(self.current_row, 1, name_and_affiliation.get(name), body)
            self.worksheet.write(self.current_row, 2, location, body)
            self.worksheet.write(self.current_row, 3, session_name, body)
            self.worksheet.write(self.current_row, 4, title, body)
            self.worksheet.write(self.current_row, 5, text, body)
            self.current_row += 1
        return item

    def open_spider(self, spider):
        self.workbook = xlsxwriter.Workbook('task.xlsx')
        self.worksheet = self.workbook.add_worksheet()

        self.worksheet.set_column(0, 0, 30)
        self.worksheet.set_column(1, 1, 40)
        self.worksheet.set_column(2, 3, 20)
        self.worksheet.set_column(4, 4, 50)
        self.worksheet.set_column(5, 5, 80)

        header = self.workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#4682b4',
            'border': 6,
            'text_wrap': True,
            'font_size': 10
        })
        self.worksheet.merge_range('A1:C1', 'About the person', header)
        self.worksheet.merge_range('D1:F1', 'About the session/topic', header)

        self.worksheet.write('A2', 'Name (incl. titles if any mentioned)', header)
        self.worksheet.write('B2', 'Affiliation(s) Name(s)', header)
        self.worksheet.write('C2', 'Person\'s Location', header)

        self.worksheet.write('D2', 'Session Name', header)
        self.worksheet.write('E2', 'Topic Title', header)
        self.worksheet.write('F2', 'Presentation Abstract', header)

    def close_spider(self, spider):
        self.workbook.close()

