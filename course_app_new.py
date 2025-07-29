import streamlit as st
import pandas as pd

def calculate_rank(df):
    df = df.copy()
    df['Rank'] = df.sort_values(
        by=['Sem3', 'Sem2', 'Sem1', 'PlusTwo', 'Name'],
        ascending=[False, False, False, False, True]
    ).reset_index().index + 1
    return df

def allot_courses(df, preferences, course_df):
    allotment = []
    seats = course_df.set_index("Course")["Seats"].to_dict()
    df['Allotted'] = None
    for idx, row in df.iterrows():
        prefs = preferences.loc[row["Candidate Code"]].dropna().tolist()
        # Handle case where student gives same preference repeatedly
        prefs = list(dict.fromkeys(prefs))  # remove duplicates
        for course in prefs:
            if seats.get(course, 0) > 0:
                df.at[idx, "Allotted"] = course
                seats[course] -= 1
                break
    return df

def get_coursewise_lists(allotment):
    return allotment.groupby("Allotted").apply(lambda g: g.sort_values("Rank")).reset_index(drop=True)

def get_departmentwise_lists(allotment):
    dept_map = {}
    for course in allotment["Allotted"].dropna().unique():
        department = course.split("-")[0].strip() if "-" in course else course
        dept_map[course] = department
    allotment["Department"] = allotment["Allotted"].map(dept_map)
    return allotment.groupby("Department").apply(lambda g: g.sort_values("Rank")).reset_index(drop=True)

st.title("Open Course Allotment System")
st.markdown("Developed by **Dr. Rakesh Chandran S.B**, Assistant Professor, Department of Physics, S.D College, Alappuzha © 2025")

student_file = st.file_uploader("Upload Student Preference File (CSV)", type="csv")
course_file = st.file_uploader("Upload Course & Seat File (CSV)", type="csv")

if student_file and course_file:
    try:
        students = pd.read_csv(student_file)
        courses = pd.read_csv(course_file)

        course_list = courses["Course"].tolist()
        preference_columns = [col for col in students.columns if col.startswith("Preference")]

        preferences = students.set_index("Candidate Code")[preference_columns]
        students_info = students[['Candidate Code', 'Name', 'Sem1', 'Sem2', 'Sem3', 'PlusTwo']]

        ranked = calculate_rank(students_info)
        final = allot_courses(ranked, preferences, courses)

        st.success("Allotment completed successfully.")

        # File 1: Final with rank and allotment
        csv1 = final.to_csv(index=False).encode()
        # File 2: Course-wise list
        csv2 = get_coursewise_lists(final).to_csv(index=False).encode()
        # File 3: Department-wise list
        csv3 = get_departmentwise_lists(final).to_csv(index=False).encode()

        st.download_button("📥 Download Final Allotment with Ranks", csv1, "final_allotment.csv", "text/csv")
        st.download_button("📥 Download Course-wise Allotment List", csv2, "coursewise_allotment.csv", "text/csv")
        st.download_button("📥 Download Department-wise Allotment List", csv3, "departmentwise_allotment.csv", "text/csv")
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please upload both required files.")
