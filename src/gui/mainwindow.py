from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QMainWindow, QTreeView, QAbstractItemView

from ..backend.data_service import DataService
from ..backend.models import Company
from .treemodel import TreeModel

MAIN_WINDOW_HEIGHT = 800

MAIN_WINDOW_WIDTH = 1200


class MainWindow(QMainWindow):
    """Main window of GUI"""
    # pylint: disable=too-few-public-methods

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Next Job")
        self.resize(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)

        self.view = QTreeView()
        self.view.setAlternatingRowColors(True)
        self.view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.view.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.view.setAllColumnsShowFocus(True)
        self.view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.view.doubleClicked.connect(self._on_row_double_clicked)
        self.setCentralWidget(self.view)

        headers = ["Title", "Details", "Recruiter(s)/Interviewer(s)"]
        self.data_service = DataService()
        self._insert_init_data()
        self.tree_model = TreeModel(headers, self.data_service.get_companies(), self)

        self.view.setModel(self.tree_model)
        self.view.setColumnWidth(0, int(MAIN_WINDOW_WIDTH / 3))
        self.view.setColumnWidth(1, int(MAIN_WINDOW_WIDTH / 3))
        self.view.setColumnWidth(2, int(MAIN_WINDOW_WIDTH / 3))

    def _on_row_double_clicked(self, index: QModelIndex):
        """Temporary method to show double-clicked items, need to handle properly"""
        item = self.tree_model.get_item(index)
        print(f"Double clicked on: {item.item_data}")

    def _insert_init_data(self):
        """Temporary method to insert some initial test data"""
        external_company = {
            "name": "Microsoft",
            "website": "https://www.microsoft.com",
            "recruiters": [
                {
                    "name": "Bill Gates",
                    "role": "Founder & CEO",
                    "email": "Jqk2g@example.com",
                    "title": "Mr"
                }
            ],
            "roles": [
                {
                    "title": "Software Engineer",
                    "applied_date": "2022-01-01",
                    "employment_type": "Full time",
                    "work_location": "Hybrid",
                    "description": "I am a software engineer.",
                    "interviews": [
                        {
                            "sequence": 1,
                            "title": "Initial Interview",
                            "type": "Recruiter",
                            "date": "2022-01-01",
                            "interviewers": [
                                {
                                    "name": "Bill Gates",
                                    "role": "Founder & CEO",
                                    "email": "Jqk2g@example.com",
                                    "title": "Mr"
                                }
                            ]
                        },
                        {
                            "sequence": 2,
                            "title": "Technical",
                            "type": "Code technical",
                            "date": "2022-01-04",
                            "interviewers": [
                                {
                                    "name": "Linus",
                                    "role": "Linux author",
                                    "email": "Jqk2g@example.com",
                                    "title": "Mr"
                                },
                                {
                                    "name": "Jack Darcy",
                                    "role": "CEO",
                                    "email": "jack@darcy.com",
                                    "title": "Mr",
                                    "description": "Just as as a listener"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        company = Company(**external_company)
        self.data_service.save_company(company)
