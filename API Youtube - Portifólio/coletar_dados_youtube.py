import os
import pandas as pd
from googleapiclient.discovery import build
from tqdm import tqdm

def ler_api_key():
    """Lê a chave de API de um arquivo de texto na mesma pasta do script."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        key_path = os.path.join(script_dir, 'api_key.txt')
        with open(key_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Erro: Arquivo 'api_key.txt' não encontrado na mesma pasta do script.")
        return None

def get_channel_id_from_handle(youtube, handle):
    """Busca o ID de um canal a partir do seu handle (ex: @Canaltech)."""
    print(f"Buscando ID do canal para o handle: {handle}")
    try:
        # ===== MUDANÇA DE SINTAXE APLICADA AQUI =====
        res = youtube.list(q=handle, type='channel', part='id', maxResults=1).execute()
        if res['items']:
            channel_id = res['items'][0]['id']['channelId']
            print(f"ID encontrado: {channel_id}")
            return channel_id
        else:
            print("Nenhum canal encontrado para este handle.")
            return None
    except Exception as e:
        print(f"Ocorreu um erro ao buscar o ID do canal: {e}")
        return None

def get_channel_videos(youtube, channel_id):
    """Busca todos os IDs de vídeos de um canal, lidando com paginação."""
    # ===== MUDANÇA DE SINTAXE APLICADA AQUI =====
    res = youtube.channels.list(id=channel_id, part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    video_ids = []
    next_page_token = None
    print("Buscando todos os IDs de vídeos do canal...")
    while True:
        # ===== MUDANÇA DE SINTAXE APLICADA AQUI =====
        res = youtube.playlistItems.list(playlistId=playlist_id,
                                           part='contentDetails',
                                           maxResults=50,
                                           pageToken=next_page_token).execute()
        
        video_ids.extend([item['contentDetails']['videoId'] for item in res['items']])
        next_page_token = res.get('nextPageToken')
        if next_page_token is None:
            break
            
    return video_ids

def get_video_details(youtube, video_ids):
    """Busca os detalhes (estatísticas e snippets) de uma lista de vídeos."""
    all_video_stats = []
    print(f"Buscando detalhes de {len(video_ids)} vídeos...")
    for i in tqdm(range(0, len(video_ids), 50)):
        # ===== MUDANÇA DE SINTAXE APLICADA AQUI =====
        res = youtube.videos.list(id=','.join(video_ids[i:i+50]),
                                    part='snippet,statistics,contentDetails').execute()
        
        for item in res['items']:
            stats = {
                'id_video': item['id'],
                'titulo': item['snippet']['title'],
                'data_publicacao': item['snippet']['publishedAt'],
                'descricao': item['snippet']['description'],
                'tags': item['snippet'].get('tags', []),
                'duracao': item['contentDetails']['duration'],
                'visualizacoes': int(item['statistics'].get('viewCount', 0)),
                'likes': int(item['statistics'].get('likeCount', 0)),
                'comentarios': int(item['statistics'].get('commentCount', 0))
            }
            all_video_stats.append(stats)
            
    return all_video_stats

if __name__ == '__main__':
    API_KEY = ler_api_key()
    
    if API_KEY:
        CHANNEL_HANDLE = '@Canaltech'
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        
        channel_id = get_channel_id_from_handle(youtube, CHANNEL_HANDLE)
        
        if channel_id:
            video_ids_list = get_channel_videos(youtube, channel_id)
            video_details_list = get_video_details(youtube, video_ids_list)
            
            print("Criando DataFrame e salvando em CSV...")
            df = pd.DataFrame(video_details_list)
            df['data_publicacao'] = pd.to_datetime(df['data_publicacao'])
            
            output_filename = 'youtube_canaltech_data.csv'
            df.to_csv(output_filename, index=False, encoding='utf-8')
            
            print(f"\nProcesso concluído com sucesso!")
            print(f"Os dados de {len(df)} vídeos foram salvos em '{output_filename}'.")