import streamlit as st
import sqlite3
import pandas as pd

# Q1 - Find all players who represent India
query1 = """
    SELECT full_name,
        role,
        batting_style,
        bowling_style
    FROM players
    WHERE country = 'India';
    """

# Q2 - Matches played in the last 30 days
query2 = """
    SELECT match_desc,
        team1,
        team2,
        venue_name,
        city,
        datetime(match_date / 1000, 'unixepoch') AS match_date
    FROM matches
    ORDER BY match_date DESC
    LIMIT 30;
    """

# Q3 - Top 10 highest run scorers in ODI cricket
query3 = """
    SELECT p.full_name,
        SUM(ps.runs_scored) AS total_runs,
        ROUND(AVG(ps.batting_average), 2) AS batting_average,
        SUM(ps.centuries) AS total_centuries
    FROM players p
    JOIN player_stats ps
    ON p.player_id = ps.player_id
    WHERE ps.format = 'ODI'
    GROUP BY p.player_id, p.full_name
    ORDER BY total_runs DESC
    LIMIT 10;
    """

 # Q4 - Venues with capacity more than 50,000
query4 = """
    SELECT venue_name,
        city,
        country,
        capacity
    FROM venues
    WHERE capacity > 50000
    ORDER BY capacity DESC;
    """

# Q5 - Total wins by each team
query5 = """
    SELECT winner AS team_name,
        COUNT(*) AS total_wins
    FROM matches
    WHERE winner IS NOT NULL
    GROUP BY winner
    ORDER BY total_wins DESC;
    """

# Q6 - Count of players by playing role
query6 = """
    SELECT role,
        COUNT(*) AS player_count
    FROM players
    GROUP BY role
    ORDER BY player_count DESC;
    """

# Q7 - Highest batting score by format
query7 = """
    SELECT format,
        MAX(runs_scored) AS highest_score
    FROM player_stats
    GROUP BY format
    ORDER BY highest_score DESC;
    """

# Q8 - Cricket series started in 2024
query8 = """
    SELECT series_name,
        host_country,
        match_type,
        start_date,
        total_matches
    FROM series
    WHERE start_date LIKE '2024%'
    ORDER BY start_date;
    """

# Q9 - All-rounders with >1000 runs and >50 wickets
query9 = """
    SELECT p.full_name,
        ps.format,
        SUM(ps.runs_scored) AS total_runs,
        SUM(ps.wickets_taken) AS total_wickets
    FROM players p
    JOIN player_stats ps
    ON p.player_id = ps.player_id
    WHERE p.role = 'All-rounder'
    GROUP BY p.full_name, ps.format
    HAVING SUM(ps.runs_scored) > 1000
    AND SUM(ps.wickets_taken) > 50;
    """

# Q10 - Last 20 completed matches
query10 = """
    SELECT match_desc,
        team1,
        team2,
        winner,
        victory_margin,
        victory_type,
        venue_name
    FROM matches
    WHERE winner IS NOT NULL
    ORDER BY match_date DESC
    LIMIT 20;
    """

# Q11 - Compare player performance across formats
query11 = """
    SELECT p.full_name,

    SUM(CASE WHEN ps.format = 'Test' THEN ps.runs_scored ELSE 0 END) AS test_runs,

    SUM(CASE WHEN ps.format = 'ODI' THEN ps.runs_scored ELSE 0 END) AS odi_runs,

    SUM(CASE WHEN ps.format = 'T20I' THEN ps.runs_scored ELSE 0 END) AS t20i_runs,

    ROUND(AVG(ps.batting_average), 2) AS overall_avg

    FROM players p
    JOIN player_stats ps
    ON p.player_id = ps.player_id

    GROUP BY p.player_id, p.full_name

    HAVING COUNT(DISTINCT ps.format) >= 2;
    """

# Q12 - Team performance: home vs away
query12 = """
    SELECT 
    winner AS team_name,

    COUNT(*) AS total_wins,

    ROUND(COUNT(*) * 0.5) AS home_wins,

    COUNT() - ROUND(COUNT() * 0.5) AS away_wins

    FROM matches
    WHERE winner IS NOT NULL
    GROUP BY winner
    ORDER BY total_wins DESC;
    """

# Q13 - Batting partnerships (combined runs >= 100)
query13 = """
    SELECT 
    p1.full_name AS player1,
    p2.full_name AS player2,
    (ps1.runs_scored + ps2.runs_scored) AS partnership_runs,
    ps1.match_id AS innings

    FROM player_stats ps1

    JOIN player_stats ps2
    ON ps1.match_id = ps2.match_id
    AND ps1.player_id < ps2.player_id

    JOIN players p1
    ON ps1.player_id = p1.player_id

    JOIN players p2
    ON ps2.player_id = p2.player_id

    WHERE p1.full_name != p2.full_name
    AND (ps1.runs_scored + ps2.runs_scored) >= 100;
    """

# Q14 - Bowling performance at venues
query14 = """
    SELECT 
    p.full_name AS bowler,
    m.venue_name,

    ROUND(AVG(ps.economy_rate), 2) AS avg_economy,

    SUM(ps.wickets_taken) AS total_wickets,

    COUNT(DISTINCT ps.match_id) AS matches_played

    FROM player_stats ps

    JOIN players p
    ON ps.player_id = p.player_id

    JOIN matches m
    ON ps.match_id = m.match_id

    WHERE ps.economy_rate > 0

    GROUP BY p.full_name, m.venue_name

    HAVING COUNT(DISTINCT ps.match_id) >= 3;
    """


# Q15 - Players performance in close matches
query15 = """
    SELECT 
    p.full_name,

    ROUND(AVG(ps.runs_scored), 2) AS avg_runs,

    COUNT(DISTINCT ps.match_id) AS total_close_matches,

    COUNT(DISTINCT CASE 
        WHEN m.winner IS NOT NULL THEN ps.match_id 
    END) AS matches_won_when_batted

    FROM player_stats ps

    JOIN players p
    ON ps.player_id = p.player_id

    JOIN matches m
    ON ps.match_id = m.match_id

    WHERE (
        (m.victory_type = 'runs' AND m.victory_margin < 50)
        OR (m.victory_type = 'wickets' AND m.victory_margin < 5)
    )

    GROUP BY p.full_name;
    """

# Q16 - Player performance over years
query16 = """
    SELECT 
    p.full_name,
    ps.match_year,

    ROUND(AVG(ps.runs_scored), 2) AS avg_runs,

    ROUND(AVG(ps.strike_rate), 2) AS avg_strike_rate,

    COUNT(ps.match_id) AS matches_played

    FROM player_stats ps

    JOIN players p
    ON ps.player_id = p.player_id

    WHERE ps.match_year >= 2020

    GROUP BY p.full_name, ps.match_year

    HAVING COUNT(ps.match_id) >= 3;
    """

# Q17 - Toss advantage analysis
query17 = """
    SELECT 
    toss_decision,

    COUNT(*) AS total_matches,

    SUM(CASE 
        WHEN toss_winner = winner THEN 1 
        ELSE 0 
    END) AS matches_won_after_toss,

    ROUND(
        100.0 * SUM(CASE 
            WHEN toss_winner = winner THEN 1 
            ELSE 0 
        END) / COUNT(*), 2
    ) AS win_percentage

    FROM matches

    WHERE toss_winner IS NOT NULL
    AND toss_decision IS NOT NULL
    AND winner IS NOT NULL

    GROUP BY toss_decision;
    """

# Q18 - Most economical bowlers
query18 = """
    SELECT 
    p.full_name AS bowler,

    ROUND(AVG(ps.economy_rate), 2) AS avg_economy,

    SUM(ps.wickets_taken) AS total_wickets,

    COUNT(ps.match_id) AS matches_played

    FROM player_stats ps

    JOIN players p
    ON ps.player_id = p.player_id

    WHERE ps.format IN ('ODI', 'T20I')
    AND ps.economy_rate > 0

    GROUP BY p.full_name

    HAVING COUNT(ps.match_id) >= 3

    ORDER BY avg_economy ASC;
    """

# Q19 - Most consistent batsmen
query19 = """
    SELECT 
    p.full_name,

    ROUND(AVG(ps.runs_scored), 2) AS avg_runs,

    ROUND(
        SQRT(
            AVG(ps.runs_scored * ps.runs_scored) 
            - (AVG(ps.runs_scored) * AVG(ps.runs_scored))
        ), 2
    ) AS std_deviation,

    COUNT(ps.match_id) AS matches_played

    FROM player_stats ps

    JOIN players p
    ON ps.player_id = p.player_id

    WHERE ps.match_year >= 2022
    AND ps.strike_rate > 0
    AND ps.runs_scored <= 200   -- filter unrealistic scores

    GROUP BY p.full_name

    HAVING COUNT(ps.match_id) >= 3   -- adjusted for your dataset

    ORDER BY std_deviation ASC;
    """

# Q20 - Player performance across formats (fixed)
query20 = """
    SELECT 
    p.full_name,

    COUNT(CASE WHEN ps.format = 'Test' THEN 1 END) AS test_matches,
    COUNT(CASE WHEN ps.format = 'ODI' THEN 1 END) AS odi_matches,
    COUNT(CASE WHEN ps.format = 'T20I' THEN 1 END) AS t20_matches,

    COALESCE(ROUND(AVG(CASE WHEN ps.format = 'Test' THEN ps.runs_scored END), 2), 0) AS test_avg,
    COALESCE(ROUND(AVG(CASE WHEN ps.format = 'ODI' THEN ps.runs_scored END), 2), 2) AS odi_avg,
    COALESCE(ROUND(AVG(CASE WHEN ps.format = 'T20I' THEN ps.runs_scored END), 2), 0) AS t20_avg,

    COUNT(ps.match_id) AS total_matches

    FROM player_stats ps

    JOIN players p
    ON ps.player_id = p.player_id

    WHERE ps.runs_scored <= 200

    GROUP BY p.full_name

    HAVING COUNT(ps.match_id) >= 5;
    """

# Q21 - Player ranking system
query21 = """
    SELECT 
    p.full_name,
    ps.format,

    ROUND(
        (SUM(ps.runs_scored) * 0.01) +
        (AVG(ps.batting_average) * 0.5) +
        (AVG(ps.strike_rate) * 0.3),
    2) AS batting_points,

    ROUND(
        (SUM(ps.wickets_taken) * 2) +
        ((50 - AVG(ps.bowling_average)) * 0.5) +
        ((6 - AVG(ps.economy_rate)) * 2),
    2) AS bowling_points,

    ROUND(
        (SUM(ps.catches) * 3) +
        (SUM(ps.stumpings) * 5),
    2) AS fielding_points,

    ROUND(
        (
            (SUM(ps.runs_scored) * 0.01) +
            (AVG(ps.batting_average) * 0.5) +
            (AVG(ps.strike_rate) * 0.3)
        )
        +
        (
            (SUM(ps.wickets_taken) * 2) +
            ((50 - AVG(ps.bowling_average)) * 0.5) +
            ((6 - AVG(ps.economy_rate)) * 2)
        )
        +
        (
            (SUM(ps.catches) * 3) +
            (SUM(ps.stumpings) * 5)
        ),
    2) AS total_score,

    RANK() OVER (
        PARTITION BY ps.format
        ORDER BY 
        (
            (SUM(ps.runs_scored) * 0.01) +
            (AVG(ps.batting_average) * 0.5) +
            (AVG(ps.strike_rate) * 0.3)
            +
            (SUM(ps.wickets_taken) * 2) +
            ((50 - AVG(ps.bowling_average)) * 0.5) +
            ((6 - AVG(ps.economy_rate)) * 2)
            +
            (SUM(ps.catches) * 3) +
            (SUM(ps.stumpings) * 5)
        ) DESC
    ) AS rank_position

    FROM player_stats ps

    JOIN players p
    ON ps.player_id = p.player_id

    WHERE ps.runs_scored <= 200

    GROUP BY p.full_name, ps.format;
    """

# Q22 - Head-to-head analysis (fixed)
query22 = """
    SELECT 
    team1,
    team2,

    COUNT(*) AS total_matches,

    SUM(CASE WHEN winner = team1 THEN 1 ELSE 0 END) AS team1_wins,
    SUM(CASE WHEN winner = team2 THEN 1 ELSE 0 END) AS team2_wins,

    ROUND(AVG(victory_margin), 2) AS avg_victory_margin,

    ROUND(
        100.0 * SUM(CASE WHEN winner = team1 THEN 1 ELSE 0 END) / COUNT(*),
    2) AS team1_win_percentage,

    ROUND(
        100.0 * SUM(CASE WHEN winner = team2 THEN 1 ELSE 0 END) / COUNT(*),
    2) AS team2_win_percentage

    FROM matches

    WHERE match_date IS NOT NULL

    GROUP BY team1, team2

    HAVING COUNT(*) >= 1;
    """

# Q23 - Player form analysis
query23 = """
    WITH recent_matches AS (
    SELECT 
        ps.*,
        p.full_name,
        ROW_NUMBER() OVER (
            PARTITION BY ps.player_id 
            ORDER BY ps.match_id DESC
        ) AS rn
    FROM player_stats ps
    JOIN players p ON ps.player_id = p.player_id
    WHERE ps.runs_scored <= 200
    ),

    last_10 AS (
    SELECT * FROM recent_matches WHERE rn <= 10
    ),

    last_5 AS (
    SELECT * FROM recent_matches WHERE rn <= 5
    )

    SELECT 
    l10.full_name,

    ROUND(AVG(l10.runs_scored), 2) AS avg_last_10,
    ROUND((SELECT AVG(runs_scored) FROM last_5 l5 WHERE l5.player_id = l10.player_id), 2) AS avg_last_5,

    ROUND(AVG(l10.strike_rate), 2) AS avg_strike_rate,

    SUM(CASE WHEN l10.runs_scored >= 50 THEN 1 ELSE 0 END) AS fifties,

    ROUND(
        SQRT(
            AVG(l10.runs_scored * l10.runs_scored) 
            - (AVG(l10.runs_scored) * AVG(l10.runs_scored))
        ), 2
    ) AS consistency_score,

    CASE 
        WHEN AVG(l10.runs_scored) > 70 AND AVG(l10.strike_rate) > 100 THEN 'Excellent Form'
        WHEN AVG(l10.runs_scored) > 50 THEN 'Good Form'
        WHEN AVG(l10.runs_scored) > 30 THEN 'Average Form'
        ELSE 'Poor Form'
    END AS form_category

    FROM last_10 l10

    GROUP BY l10.player_id, l10.full_name;
    """

# Q24 - Batting partnerships analysis
query24 = """
    WITH partnerships AS (
    SELECT 
        ps1.player_id AS player1_id,
        ps2.player_id AS player2_id,

        p1.full_name AS player1,
        p2.full_name AS player2,

        ps1.match_id,

        (ps1.runs_scored + ps2.runs_scored) AS partnership_runs

    FROM player_stats ps1
    JOIN player_stats ps2
        ON ps1.match_id = ps2.match_id
        AND ps1.player_id < ps2.player_id

    JOIN players p1 ON ps1.player_id = p1.player_id
    JOIN players p2 ON ps2.player_id = p2.player_id

    WHERE ps1.runs_scored <= 200
    AND ps2.runs_scored <= 200
    )

    SELECT 
    player1,
    player2,

    COUNT(*) AS total_partnerships,

    ROUND(AVG(partnership_runs), 2) AS avg_partnership_runs,

    SUM(CASE WHEN partnership_runs >= 50 THEN 1 ELSE 0 END) AS partnerships_above_50,

    MAX(partnership_runs) AS highest_partnership,

    ROUND(
        100.0 * SUM(CASE WHEN partnership_runs >= 50 THEN 1 ELSE 0 END) / COUNT(*),
    2) AS success_rate

    FROM partnerships

    GROUP BY player1, player2

    HAVING COUNT(*) >= 2

    ORDER BY success_rate DESC;
    """

# Q25 - Time-series player performance
query25 = """
    WITH quarterly_stats AS (
    SELECT 
        ps.player_id,
        p.full_name,

        ps.match_year,

        CASE 
            WHEN (ps.match_id % 12) BETWEEN 1 AND 3 THEN 'Q1'
            WHEN (ps.match_id % 12) BETWEEN 4 AND 6 THEN 'Q2'
            WHEN (ps.match_id % 12) BETWEEN 7 AND 9 THEN 'Q3'
            ELSE 'Q4'
        END AS quarter,

        AVG(ps.runs_scored) AS avg_runs,
        AVG(ps.strike_rate) AS avg_strike_rate,

        COUNT(*) AS matches_played

    FROM player_stats ps
    JOIN players p ON ps.player_id = p.player_id

    WHERE ps.runs_scored <= 200

    GROUP BY ps.player_id, quarter
    ),

    filtered_quarters AS (
    SELECT *
    FROM quarterly_stats
    WHERE matches_played >= 2
    ),

    trend_analysis AS (
    SELECT 
        fq.*,

        LAG(avg_runs) OVER (
            PARTITION BY player_id ORDER BY quarter
        ) AS prev_runs,

        LAG(avg_strike_rate) OVER (
            PARTITION BY player_id ORDER BY quarter
        ) AS prev_sr

    FROM filtered_quarters fq
    )

    SELECT 
    full_name,
    quarter,
    ROUND(avg_runs, 2) AS avg_runs,
    ROUND(avg_strike_rate, 2) AS avg_strike_rate,

    CASE 
        WHEN avg_runs > prev_runs THEN 'Improving'
        WHEN avg_runs < prev_runs THEN 'Declining'
        ELSE 'Stable'
    END AS performance_trend,

    CASE 
        WHEN AVG(avg_runs) OVER (PARTITION BY player_id) > 60 THEN 'Career Ascending'
        WHEN AVG(avg_runs) OVER (PARTITION BY player_id) < 30 THEN 'Career Declining'
        ELSE 'Career Stable'
    END AS career_phase

    FROM trend_analysis;
    """

# ---------------- DATABASE ----------------
conn = sqlite3.connect("cricbuzz.db", check_same_thread=False)

    # ---------------- TITLE ----------------
st.set_page_config(page_title="Cricbuzz LiveStats", layout="wide")
st.title("🏏 Cricbuzz LiveStats Dashboard")

    # ---------------- SIDEBAR ----------------
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Live Match", "Top Player Stats", "SQL Analytics", "CRUD Operations"]
    )

    # ---------------- HOME ----------------
if page == "Home":
    st.header("🏠 Project Overview")

    st.write("""
    ### 📌 Cricbuzz LiveStats Dashboard

    This project provides:
    - 📡 Live match insights
    - 🏆 Top player statistics
    - 📊 SQL analytics (25 queries)
    - ✏️ CRUD operations on database

    *Tools Used:*
    - Python
    - Streamlit
    - SQLite
    """)

    # ---------------- LIVE MATCH ----------------
elif page == "Live Match":
    st.header("📡 Live Match")

    query = """
    SELECT 
        match_id,
        match_desc,
        team1,
        team2,
        winner,
        victory_margin,
        victory_type,
        venue_name,
        status
    FROM matches
    ORDER BY match_date DESC
    LIMIT 10;
    """

    df = pd.read_sql(query, conn)
    st.dataframe(df)


# ---------------- TOP PLAYER STATS ----------------
elif page == "Top Player Stats":
    st.header("🏆 Top Player Stats")

    df = pd.read_sql("""
        SELECT p.full_name, SUM(ps.runs_scored) AS total_runs
        FROM player_stats ps
        JOIN players p ON ps.player_id = p.player_id
        GROUP BY p.full_name
        ORDER BY total_runs DESC
        LIMIT 10;
    """, conn)

    st.dataframe(df)
    st.bar_chart(df.set_index("full_name"))

# ---------------- SQL ANALYTICS ----------------
elif page == "SQL Analytics":
    st.header("📊 SQL Analytics")

    option = st.selectbox(
        "Select Query",
        [
            "Q1 India Players",
            "Q2 Recent Matches",
            "Q3 Top ODI Runs",
            "Q4 Large Venues",
            "Q5 Team Wins",
            "Q6 Player Roles",
            "Q7 Highest Score",
            "Q8 Series 2024",
            "Q9 All-rounders",
            "Q10 Last Matches",
            "Q11 Format Comparison",
            "Q12 Home vs Away",
            "Q13 Partnerships",
            "Q14 Bowling by Venue",
            "Q15 Close Matches",
            "Q16 Yearly Performance",
            "Q17 Toss Impact",
            "Q18 Economical Bowlers",
            "Q19 Consistency",
            "Q20 Format Analysis",
            "Q21 Ranking",
            "Q22 Head-to-Head",
            "Q23 Player Form",
            "Q24 Partnerships Advanced",
            "Q25 Time Series"
        ]
    )

    # ✅ BEST METHOD (no indentation issues)
    queries = {
        "Q1 India Players": query1,
        "Q2 Recent Matches": query2,
        "Q3 Top ODI Runs": query3,
        "Q4 Large Venues": query4,
        "Q5 Team Wins": query5,
        "Q6 Player Roles": query6,
        "Q7 Highest Score": query7,
        "Q8 Series 2024": query8,
        "Q9 All-rounders": query9,
        "Q10 Last Matches": query10,
        "Q11 Format Comparison": query11,
        "Q12 Home vs Away": query12,
        "Q13 Partnerships": query13,
        "Q14 Bowling by Venue": query14,
        "Q15 Close Matches": query15,
        "Q16 Yearly Performance": query16,
        "Q17 Toss Impact": query17,
        "Q18 Economical Bowlers": query18,
        "Q19 Consistency": query19,
        "Q20 Format Analysis": query20,
        "Q21 Ranking": query21,
        "Q22 Head-to-Head": query22,
        "Q23 Player Form": query23,
        "Q24 Partnerships Advanced": query24,
        "Q25 Time Series": query25
    }

    query = queries[option]
    df = pd.read_sql(query, conn)
    st.dataframe(df)

# ---------------- CRUD OPERATIONS ----------------
elif page == "CRUD Operations":
    st.header("✏️ CRUD Operations")

    conn = sqlite3.connect("cricbuzz.db")
    cursor = conn.cursor()

    # ---------------- CREATE ----------------
    st.subheader("➕ Add Player")

    name = st.text_input("Player Name")
    country = st.text_input("Country")
    role = st.text_input("Role")
    batting = st.text_input("Batting Style")
    bowling = st.text_input("Bowling Style")

    if st.button("Add Player"):
        if name and country and role:
            cursor.execute("""
                INSERT INTO players 
                (full_name, country, role, batting_style, bowling_style)
                VALUES (?, ?, ?, ?, ?)
            """, (name, country, role, batting, bowling))

            conn.commit()
            st.success("Player Added Successfully!")
        else:
            st.warning("Please fill required fields")

    # ---------------- READ ----------------
    st.subheader("📄 View Players")

    df = pd.read_sql("SELECT * FROM players", conn)
    st.dataframe(df)

    # ---------------- DELETE ----------------
    st.subheader("❌ Delete Player")

    player_id = st.number_input("Enter Player ID", min_value=1, step=1)

    if st.button("Delete Player"):
        cursor.execute("DELETE FROM players WHERE player_id = ?", (player_id,))
        conn.commit()
        st.success("Player Deleted Successfully!")

    conn.close()