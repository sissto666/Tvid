import config
import sys
from PySide6.QtCore import QUrl, Qt
from PySide6.QtWidgets import (QApplication, QMainWindow, QLineEdit,
                               QToolBar, QVBoxLayout,
                               QWidget, QHBoxLayout, QPushButton, QMenu, QToolButton,QDialog,  QListWidget, QDialogButtonBox)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile, QWebEnginePage
from PySide6.QtGui import QIcon, QPalette, QColor,QPixmap
from utils.hotkey import GlobalHotkey

class BrowserWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.parent_window = parent

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # 允许所有导航请求
        if isMainFrame:
            self.parent_window.url_bar.setText(url.toString())
        return True

    def createWindow(self, type):
        # 在当前窗口打开新链接，而不是创建新窗口
        return self.parent_window.browser.page()


class BrowserWindow(QMainWindow):
    def __init__(self,):
        super().__init__()
        # 可自定义参数
        self.opacity = config.parameter['opacity']
        self.aspect_ratio = config.parameter['aspect_ratio']
        self.default_url = config.parameter['default_url']
        if config.parameter.get('recent_url'):
            self.default_url = config.parameter['recent_url']
        self.window_width = config.parameter['default_window_width']
        self.window_length = config.parameter['default_window_length']
        self.window_x = config.parameter['default_window_x']
        self.window_y = config.parameter['default_window_y']
        self.userAgent = config.parameter['UserAgent']

        # 变量
        self.running_key_list = []
        self.recent_url = None

        # 窗口初始化参数
        self.setWindowTitle("攻略视频小窗口")
        self.setGeometry(self.window_x, self.window_y, self.window_width, self.window_length)
        # 置顶
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)


        # 创建主布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建浏览器
        self.browser = QWebEngineView()
        main_layout.addWidget(self.browser)
        
        # 创建自定义工具栏
        self.toolbar = QToolBar("导航栏")
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #2c3e50;
                border: none;
                padding: 6px;
            }
            QLineEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #3498db;
                border-radius: 12px;
                padding: 5px 15px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 5px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.addToolBar(self.toolbar)

        # 创建导航控件
        self.nav_widget = QWidget()
        nav_layout = QHBoxLayout(self.nav_widget)
        nav_layout.setContentsMargins(10, 0, 10, 0)

        # 一些按钮
        self.bookmark_btn = QPushButton("收藏")
        self.bookmark_btn.clicked.connect(self.save_url)

        self.go_btn = QPushButton("访问")
        self.go_btn.setIcon(QIcon.fromTheme("go-jump"))
        self.go_btn.clicked.connect(self.navigate_to_url)

        # 创建下拉菜单按钮
        self.bookmark_dropdown = QToolButton()  
        self.bookmark_dropdown.setText("收藏夹") 
        self.bookmark_dropdown.setPopupMode(QToolButton.InstantPopup)

        # 创建菜单对象
        self.bookmark_menu = QMenu(self)
        self.bookmark_dropdown.setMenu(self.bookmark_menu)
        self.update_bookmark_menu()

        # 地址栏
        self.url_bar = QLineEdit(self.default_url)
        self.url_bar.setMinimumHeight(36)
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        # 添加控件到布局
        nav_layout.addWidget(self.url_bar)
        nav_layout.addWidget(self.go_btn)
        nav_layout.addWidget(self.bookmark_btn)
        nav_layout.addWidget(self.bookmark_dropdown)
        self.toolbar.addWidget(self.nav_widget)

        # 对浏览器配置进行一些调整
        self.change_browser_settings()

        # 快捷键绑定
        # 锁定快捷键
        self.bind_shortcut('MOD','lock_shortcuts_VK',self.hide_control)
        # 暂停
        self.bind_shortcut('MOD','start_pause_VK',self.start_pause_video)
        # 快进
        self.bind_shortcut('MOD','time_go_VK',self.time_go_video)
        # 快退
        self.bind_shortcut('MOD','time_back_VK',self.time_back_video)

    def resizeEvent(self, event):
        '''自定义窗口改变事件：用户改变窗口保持比例'''
        if event.spontaneous(): 
            new_width = event.size().width()
            expected_height = int(new_width / self.aspect_ratio)
            self.resize(new_width, expected_height)

            if new_width < 800:
                self.window_width = new_width
                self.window_length = expected_height

        else:
            super().resizeEvent(event)

    def closeEvent(self, event):
        '''自定义关闭事件'''
        # 关闭后保存数据
        config.save_parameter(
            recent_url=self.recent_url,
            default_window_width=self.window_width,
            default_window_length=self.window_length,
            default_window_x = self.window_x,
            default_window_y = self.window_y,
            )
        
        for key in self.running_key_list:
            key.stop()
        self.web_page.deleteLater()
        self.profile.deleteLater()   
        super().closeEvent(event)

    def bind_shortcut(self,config_mod,config_vk,func_name):
        '''绑定按键'''
        mod = config.parameter[config_mod]
        vk =  config.parameter[config_vk]
        shortcut = GlobalHotkey(mod,vk)
        shortcut.hotkey_triggered.connect(func_name)
        shortcut.start()
        self.running_key_list.append(shortcut)

    def change_browser_settings(self):
        '''一些浏览器配置'''
        # 建立信号
        self.browser.urlChanged.connect(self.update_url)
        self.browser.loadFinished.connect(self.update_title)

        # 持久化登录信息保存
        self.profile = QWebEngineProfile("MyCustomProfile", self)

        # 创建页面
        self.web_page = BrowserWebEnginePage(self.profile, self)
        self.browser.setPage(self.web_page)

        self.profile.setPersistentCookiesPolicy(
            QWebEngineProfile.ForcePersistentCookies)

        browser_data_file = config.browser_data_file
        self.profile.setCachePath(browser_data_file)
        self.profile.setPersistentStoragePath(browser_data_file)
        self.profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)

        # 设置用户代理
        self.profile.setHttpUserAgent(self.userAgent)

        # 配置浏览器设置
        settings = self.browser.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.navigate_to_url()

    def hide_control(self):
        '''实现隐藏(开启)边框,增加(回退)透明度,锁定(解除)窗口逻辑'''
        # 记录隐藏时窗口位置供关闭时记忆
        pos = self.pos()
        self.window_x,self.window_y = pos.x(), pos.y()

        current_flags = self.windowFlags()
        if current_flags & Qt.FramelessWindowHint:
            # 正常模式
            new_flags = current_flags & ~Qt.FramelessWindowHint & ~Qt.WindowTransparentForInput
            self.toolbar.setVisible(True)
            self.setWindowOpacity(1.0)

        else:
            # 无边框模式
            new_flags = current_flags | Qt.FramelessWindowHint | Qt.WindowTransparentForInput
            self.toolbar.setVisible(False)
            self.setWindowOpacity(self.opacity)

        self.setWindowFlags(new_flags)
        self.show()
        self.update()

    def start_pause_video(self):
        js_code = """
        var video = document.querySelector('video');
        if (video.paused) {
            video.play();
        } else {
            video.pause();
        }
        """
        self.browser.page().runJavaScript(js_code)

    def time_go_video(self):
        js_code = """
        var video = document.querySelector('video');
        video.currentTime = Math.min(video.currentTime + 10, video.duration);
        """
        self.browser.page().runJavaScript(js_code)

    def time_back_video(self):
        js_code = """
        var video = document.querySelector('video');

        if (video.currentTime <= 12) {
        video.currentTime = 0; 
    } else {
        video.currentTime = video.currentTime - 10; 
    }
        """
        self.browser.page().runJavaScript(js_code)

    def navigate_to_url(self):
        """导航到地址栏中的URL"""
        url_text = self.url_bar.text().strip()
        if not url_text:
            return
        # 添加协议前缀
        if not url_text.startswith(("http://", "https://")):
            url_text = "https://" + url_text
        self.browser.setUrl(QUrl(url_text))

    def update_url(self, url):
        """更新地址栏显示"""
        url = url.toString()
        # 更新中添加到最近url
        self.recent_url = url
        self.url_bar.setText(url)

    def update_title(self, success):
        """更新窗口标题"""
        title = self.browser.page().title()
        self.setWindowTitle(title)

    def save_url(self):
        '''保存至书签'''
        title = self.browser.page().title()
        url = self.browser.page().url().toString()
        config.read_and_write_to_bookmarks(
            file=config.bookmark_file, new_dic={title: url})
        self.update_bookmark_menu()

    def show_bookmark_manager(self):
        """显示收藏夹管理对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("收藏夹管理")
        dialog.resize(400, 300)
        layout = QVBoxLayout()
        # 创建列表显示收藏
        list_widget = QListWidget()
        if not config.bookmarks_data:
            return
        for title, url in config.bookmarks_data.items():
            list_widget.addItem(f"{title}+---+{url}")
        # 创建操作按钮
        button_box = QDialogButtonBox()
        delete_btn = button_box.addButton("删除", QDialogButtonBox.ActionRole)
        close_btn = button_box.addButton("关闭", QDialogButtonBox.RejectRole)
        # 连接信号
        delete_btn.clicked.connect(lambda: self.delete_bookmark(list_widget))
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(list_widget)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.exec()

    def delete_bookmark(self, list_widget):
        """删除选中的收藏"""
        if not list_widget.currentItem():
            return
        selected_text = list_widget.currentItem().text()
        title = selected_text.split("+---+")[0]
        if title in config.bookmarks_data:
            del config.bookmarks_data[title]
            config.read_and_write_to_bookmarks(file=config.bookmark_file)
            list_widget.takeItem(list_widget.currentRow())
            self.update_bookmark_menu()

    def update_bookmark_menu(self):
        """更新收藏夹菜单"""
        self.bookmark_menu.clear()
        bookmarks_data = config.bookmarks_data
        if not bookmarks_data:
            return
        for title, url in bookmarks_data.items():
            action = self.bookmark_menu.addAction(title)
            action.triggered.connect(
                lambda checked=False, u=url: self.navigate_to_bookmark(u))
        # 添加分隔线
        self.bookmark_menu.addSeparator()
        # 添加管理功能
        manage_action = self.bookmark_menu.addAction("管理收藏夹")
        manage_action.triggered.connect(self.show_bookmark_manager)

    def navigate_to_bookmark(self, url):
        """导航到指定书签URL"""
        if hasattr(self, 'browser') and self.browser:
            self.browser.setUrl(QUrl(url))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QPixmap(config.ico))
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(44, 62, 80))
    palette.setColor(QPalette.WindowText, QColor(236, 240, 241))
    app.setPalette(palette)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec())

