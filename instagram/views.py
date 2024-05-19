from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .forms import InstagramUserForm
import pandas as pd
import instaloader
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage

class DownloadFollowers(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        form = InstagramUserForm(request.POST, request.FILES)
        if form.is_valid():
            # mengambil file yang diupload
            uploaded_file = request.FILES['username_file']
            file_path = default_storage.save(uploaded_file.name, uploaded_file)

            # membaca username dari file
            df = pd.read_excel(file_path)
            usernames = df['Username'].tolist()

            # membuat list/array kosong untuk menyimpan data nanti
            user_dfs = []

            # Download user details
            loader = instaloader.Instaloader()

            for username in usernames:
                # mengambil post_data setiap user
                post_data = {
                    'Username': [], 'Caption': [], 'Likes': [], 'Banyak Comments': [], 'Tanggal': [],
                    'Followers': 0, 'Following': 0, 'Total Posts': 0
                }

                try:
                    profile = instaloader.Profile.from_username(loader.context, username)

                    # mengambil profile data dari username
                    post_data['Followers'] = profile.followers
                    post_data['Following'] = profile.followees
                    post_data['Total Posts'] = profile.mediacount

                    # mengambil post data dari masing-masing username
                    for post in profile.get_posts():
                        if len(post_data['Caption']) >= form.cleaned_data['num_posts_to_scrape']:
                            break  # berhenti setelah 10 data (ubah jika perlu)
                        post_data['Username'].append(username)
                        post_data['Caption'].append(post.caption)
                        post_data['Likes'].append(post.likes)
                        post_data['Banyak Comments'].append(post.comments)
                        post_data['Tanggal'].append(post.date.date())

                except instaloader.ProfileNotExistsException:
                    post_data['Followers'] = 0
                    post_data['Following'] = 0
                    post_data['Total Posts'] = 0
                    post_data['Username'].append(username)
                    post_data['Caption'].append("")
                    post_data['Likes'].append(0)
                    post_data['Banyak Comments'].append(0)
                    post_data['Tanggal'].append("")
                except Exception as e:
                    post_data['Followers'] = 0
                    post_data['Following'] = 0
                    post_data['Total Posts'] = 0
                    post_data['Username'].append(username)
                    post_data['Caption'].append("")
                    post_data['Likes'].append(0)
                    post_data['Banyak Comments'].append(0)
                    post_data['Tanggal'].append("")

                # membuat dataframe dari data yang diambil
                post_df = pd.DataFrame(post_data)

                # gabung dataframe user dengan post
                user_dfs.append(post_df)

            final_df = pd.concat(user_dfs, ignore_index=True)

            # menyimpan ke excel
            post_file_path = 'post_information.xlsx'
            with pd.ExcelWriter(post_file_path, engine='xlsxwriter') as writer:
                final_df.to_excel(writer, sheet_name='Post Information', index=False)

            # fitur download
            with open(post_file_path, 'rb') as excel_file:
                response = HttpResponse(
                    excel_file.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename=post_information.xlsx'
                return response

        else:
            return Response({'error': 'Invalid form data'}, status=status.HTTP_400_BAD_REQUEST)
