from datetime import datetime

class Order:
    def __init__(self, user_id, student_name, pizza_slices, juice_boxes, parent_volunteer, date):
        self.user_id = user_id
        self.student_name = student_name or "Unknown"
        self.pizza_slices = pizza_slices or {}
        self.juice_boxes = juice_boxes or 0
        self.parent_volunteer = parent_volunteer or False
        self.date = date
        self.timestamp = datetime.utcnow()
