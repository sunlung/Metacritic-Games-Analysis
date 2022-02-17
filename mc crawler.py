
import csv
import re
import requests

def get_html(url):
  """ Returns the HTML of the url page """

  r = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
  })
  html = r.text

  return html


def get_game_page_data(page_num, game_num, baseUrl, gameName):
  """ Fetches HTML of a particular game page and parses data from it """

  html = get_html(baseUrl + gameName + '/details')
  lines = html.split('\n')
  print('\t[%d - %d] getting game details: %s with line counts: %i' % (page_num, game_num, baseUrl + gameName + '/details', len(lines)))

  start_parse_additional_info = False
  start_parse_esrb_rating = False
  start_parse_developer = False
  start_parse_genres = False
  start_parse_ms_n=False
  start_parse_platform=False
  start_parse_user_score=False
  start_parse_meta_score=False
  start_parse_date=False
  start_parse_publisher=False
  datum={}
  datum["link"] = gameName
  n = 0
  for line in lines:
    n=n+1
    if '<th scope="row">Rating:</th>' in line:
      start_parse_esrb_rating = True
    elif start_parse_esrb_rating:
      datum['esrb_rating'] = line.split('<td>')[1].split('</td>')[0]
      start_parse_esrb_rating = False
    elif '<th scope="row">Developer:</th>' in line:
      start_parse_developer = True
    elif start_parse_developer:
      datum['developers'] = [x.strip() for x in line.split("<td>")[1].split("</td>")[0].split(',')]
      start_parse_developer = False
    elif '<th scope="row">Genre(s):</th>' in line:
      start_parse_genres = True
    elif '</td>' in line and start_parse_genres:
      datum['genres'] = [x.strip() for x in line.split('</td>')[0].split(',')]
      start_parse_genres = False
    elif '<meta property="og:title" content="' in line:
      datum['title'] = line.split('<meta property="og:title" content="')[1].split('">')[0]
    elif '<span class="platform">' in line:
      start_parse_platform = True
    elif '<a href=' not in line and start_parse_platform:
      datum['platform'] = line.strip()
      start_parse_platform = False
    elif '<span class="label">Publisher:</span>' in line:
      start_parse_publisher = True
    elif '<' not in line and start_parse_publisher:
      datum['publisher'] = line.strip()
      start_parse_publisher = False
    elif ' <span class="label">Release Date:</span>' in line:
      start_parse_date = True
    elif start_parse_date and '<span class="data" >' in line:
      datum['release_date'] = line.split('<span class="data" >')[1].split("</span>")[0].strip()
      start_parse_date = False
    elif '<div class="label">User Score</div>' in line:
      start_parse_user_score = True
    elif '<div class="' in line and start_parse_user_score:
      datum['user_score'] = line.split(">")[1].split("<")[0]
      start_parse_user_score = False
    elif '<div class="label">Metascore</div>' in line:
      start_parse_meta_score = True
    elif '<div class="' in line and start_parse_meta_score:
      if '<span itemprop="ratingValue">' in line:
        datum['meta_score'] = line.split('<span itemprop="ratingValue">')[1].split("<")[0]
      start_parse_meta_score = False
    elif '                <span class="based">based on</span>' in line:
      start_parse_ms_n = True
    elif "<span >0</span> Critic Reviews" in line and start_parse_ms_n:
      datum['num_meta_review'] = 0
      start_parse_ms_n = False
    elif "<" not in line and start_parse_ms_n:
      datum['num_meta_review'] = int(line.strip())
      start_parse_ms_n = False
    elif '<a href="' + gameName + '/user-reviews">' in line:
      datum['num_user_review'] = int(line.split("user-reviews\">")[1].split(" Ratings</a>")[0])
    elif '<img class="product_image large_image" src="' in line:
      datum['game_img_url'] = line.split('<img class="product_image large_image" src="')[1].split('" alt=')[0]
  return datum

def parse_html(page_num, base_url, html):
  """ Parses the input HTML for Pokemon Game ratings"""

  lines = html.split('\n')

  data = []
  start_parse_additional_info = False

  game_num = 1

  for line in lines:
    if '<td class="clamp-image-wrap">' in line:
      start_parse_additional_info = True
    elif '<a href="/game/' in line and start_parse_additional_info:
      detail_url = line.split('<a href="')[1].split('"><img src="')[0]
      start_parse_additional_info = False
      datum=get_game_page_data(page_num, game_num,base_url, detail_url)
      data.append(datum)
      game_num = game_num+1

  return data


def write_csv(data):
  """ Writes a CSV file of the ratings data """

  with open('data2.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['meta_score', 'title', 'platform', 'release_date', 'user_score', 'link', 'esrb_rating', 'publisher', 'developers', 'genres', 'num_meta_review', 'num_user_review', 'game_img_url'])
    writer.writeheader()
    for row in data:
      writer.writerow(row)


def main():
  base_url = 'https://www.metacritic.com'
  game_list_url = 'https://www.metacritic.com/browse/games/release-date/available/ios/date?page='
  num_pages = 121

  data = []

  for page_num in range(0, num_pages):
    url = game_list_url + str(page_num)
    html = get_html(url)
    print('Got HTML from %s. Parsing...' % url)

    page_data = parse_html(page_num + 1, base_url, html)
    print('Got %d game ratings\n' % len(page_data))

    data.extend(page_data)

  print('Writing data to CSV...\n')
  write_csv(data)

  print('Done!')


if __name__ == '__main__':
    main()
