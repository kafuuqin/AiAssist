create table alembic_version
(
    version_num varchar(32) not null
        primary key
);

create table users
(
    id            int auto_increment
        primary key,
    name          varchar(120) not null,
    email         varchar(255) not null,
    role          varchar(32)  null,
    password_hash varchar(255) not null,
    created_at    datetime     null,
    updated_at    datetime     null,
    constraint ix_users_email
        unique (email)
);

create table courses
(
    id          int auto_increment
        primary key,
    name        varchar(200) not null,
    code        varchar(50)  not null,
    term        varchar(50)  null,
    description text         null,
    owner_id    int          not null,
    created_at  datetime     null,
    constraint code
        unique (code),
    constraint courses_ibfk_1
        foreign key (owner_id) references users (id)
);

create table assignments
(
    id         int auto_increment
        primary key,
    course_id  int          not null,
    title      varchar(200) not null,
    type       varchar(50)  null,
    weight     float        null,
    full_score float        null,
    due_at     datetime     null,
    created_at datetime     null,
    constraint assignments_ibfk_1
        foreign key (course_id) references courses (id)
);

create index ix_assignments_course_id
    on assignments (course_id);

create table attendance_sessions
(
    id        int auto_increment
        primary key,
    course_id int          not null,
    title     varchar(200) not null,
    mode      varchar(50)  null,
    start_at  datetime     null,
    end_at    datetime     null,
    status    varchar(20)  null,
    constraint attendance_sessions_ibfk_1
        foreign key (course_id) references courses (id)
);

create table attendance_records
(
    id                 int auto_increment
        primary key,
    session_id         int          not null,
    student_id         int          not null,
    status             varchar(20)  null,
    evidence           varchar(255) null,
    recognized_face_id varchar(255) null,
    created_at         datetime     null,
    constraint attendance_records_ibfk_1
        foreign key (session_id) references attendance_sessions (id),
    constraint attendance_records_ibfk_2
        foreign key (student_id) references users (id)
);

create index ix_attendance_records_session_id
    on attendance_records (session_id);

create index student_id
    on attendance_records (student_id);

create index ix_attendance_sessions_course_id
    on attendance_sessions (course_id);

create index owner_id
    on courses (owner_id);

create table enrollments
(
    id             int auto_increment
        primary key,
    course_id      int         not null,
    user_id        int         not null,
    role_in_course varchar(20) null,
    status         varchar(20) null,
    created_at     datetime    null,
    constraint enrollments_ibfk_1
        foreign key (course_id) references courses (id),
    constraint enrollments_ibfk_2
        foreign key (user_id) references users (id)
);

create index ix_enrollments_course_id
    on enrollments (course_id);

create index ix_enrollments_user_id
    on enrollments (user_id);

create table grades
(
    id            int auto_increment
        primary key,
    assignment_id int      not null,
    student_id    int      not null,
    score         float    not null,
    comment       text     null,
    graded_at     datetime null,
    constraint grades_ibfk_1
        foreign key (assignment_id) references assignments (id),
    constraint grades_ibfk_2
        foreign key (student_id) references users (id)
);

create index ix_grades_assignment_id
    on grades (assignment_id);

create index student_id
    on grades (student_id);

create table materials
(
    id          int auto_increment
        primary key,
    course_id   int          not null,
    title       varchar(255) not null,
    description text         null,
    path        varchar(500) null,
    file_type   varchar(50)  null,
    size        int          null,
    tags        json         null,
    uploader_id int          not null,
    created_at  datetime     null,
    constraint materials_ibfk_1
        foreign key (course_id) references courses (id),
    constraint materials_ibfk_2
        foreign key (uploader_id) references users (id)
);

create index ix_materials_course_id
    on materials (course_id);

create index uploader_id
    on materials (uploader_id);

create table polls
(
    id         int auto_increment
        primary key,
    course_id  int          not null,
    question   varchar(255) not null,
    options    json         null,
    is_active  tinyint(1)   null,
    created_at datetime     null,
    constraint polls_ibfk_1
        foreign key (course_id) references courses (id)
);

create table poll_votes
(
    id           int auto_increment
        primary key,
    poll_id      int      not null,
    user_id      int      not null,
    option_index int      not null,
    created_at   datetime null,
    constraint poll_votes_ibfk_1
        foreign key (poll_id) references polls (id),
    constraint poll_votes_ibfk_2
        foreign key (user_id) references users (id)
);

create index ix_poll_votes_poll_id
    on poll_votes (poll_id);

create index user_id
    on poll_votes (user_id);

create index ix_polls_course_id
    on polls (course_id);


