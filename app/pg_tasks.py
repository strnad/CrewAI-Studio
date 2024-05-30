import streamlit as st
from streamlit import session_state as ss
from my_task import MyTask
import db_utils

class PageTasks:
    def __init__(self):
        self.name = "Tasks"

    def create_task(self):
        task = MyTask()
        if 'tasks' not in ss:
            ss.tasks = []
        ss.tasks.append(task)
        task.edit = True
        db_utils.save_task(task)  # Save task to database
        return task

    def draw(self):
        with st.container():
            st.subheader(self.name)
            editing = False
            if 'tasks' not in ss:
                ss.tasks = db_utils.load_tasks()  # Load tasks from database
            for task in ss.tasks:
                task.draw()
                if task.edit:
                    editing = True
            if len(ss.tasks) == 0:
                st.write("No tasks defined yet.")
            st.button('Create task', on_click=self.create_task, disabled=editing)
