from screeninfo import get_monitors


def setup_window_position(self, monitor_selected):
    monitors = get_monitors()
    selected_monitor = (
        monitors[monitor_selected]
        if 0 <= monitor_selected < len(monitors)
        else monitors[0]
    )
    x = selected_monitor.x + (selected_monitor.width - self.WINDOW_WIDTH) // 2
    y = selected_monitor.y + (selected_monitor.height - self.WINDOW_HEIGHT) // 2

    return x, y
