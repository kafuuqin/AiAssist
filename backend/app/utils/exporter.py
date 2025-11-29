import csv
import io


TEMPLATE_HEADER = [
    "# 使用说明：student_id/assignment_id/score 为必填列；comment 可选；score 0-100",
    "# 示例：student_id,assignment_id,score,comment",
]


def grades_to_csv(grades):
    """
    导出成绩 CSV，附简单说明行与表头
    字段：student_id, assignment_id, score, comment, graded_at
    """
    output = io.StringIO()
    writer = csv.writer(output)
    for line in TEMPLATE_HEADER:
        writer.writerow([line])
    writer.writerow(["student_id", "assignment_id", "score", "comment", "graded_at"])
    for g in grades:
        writer.writerow(
            [
                g.student_id,
                g.assignment_id,
                g.score,
                (g.comment or "").replace("\n", " "),
                g.graded_at.isoformat() if g.graded_at else "",
            ]
        )
    return output.getvalue()


def grades_template_csv(assignment_id=None):
    """
    生成导入模板 CSV，包含必填/可选列说明和示例数据
    """
    output = io.StringIO()
    writer = csv.writer(output)
    for line in TEMPLATE_HEADER:
        writer.writerow([line])
    writer.writerow(["student_id", "assignment_id", "score", "comment"])
    example_assignment = assignment_id or "A001"
    writer.writerow(["S001", example_assignment, 95, "示例评语"])
    writer.writerow(["S002", example_assignment, 88, ""])
    writer.writerow(["S003", example_assignment, 72, "迟交扣分"])
    return output.getvalue()
