from app.utils.csv_parser import parse_csv

from flask import Blueprint, render_template, url_for, request, redirect

from app.modules.database.create_tables import TbCreator


upload_csv = Blueprint('upload_csv', __name__)


@upload_csv.route('/upload_csv', methods=['POST', 'GET'])
def add_csv():
    if request.method == 'POST':
        csv_prefectures = request.files['prefectures']
        table_prefectures = parse_csv(csv_prefectures)
        csv_cities = request.files['cities']
        table_cities = parse_csv(csv_cities)
        csv_users = request.files['users']
        table_users = parse_csv(csv_users)

        if csv_prefectures and csv_cities and csv_users:
            TbCreator.create_all_start_tables(
                prefectures=table_prefectures,
                cities=table_cities,
                users=table_users
            )
        return redirect(url_for('person_lk.person_cabinet'))
    """страничка для загрузки csv"""
    return render_template('main/upload_csv.html')
