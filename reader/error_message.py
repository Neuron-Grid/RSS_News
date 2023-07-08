# 辞書型でエラーメッセージを定義
ERROR_MESSAGES = {
    'date_parse_error' : '日付のパースに失敗しました。\n RSSフィードの日付のフォーマットが正しくない場合に発生します。\n もしくは、フィードのパースに失敗した場合に発生します。',
    'entry_not_found_error' : '指定されたURLのフィードにエントリがありません。',
    'date_format_error' : 'フィードの日付のフォーマットが正しくありません。',
    'not_found_error' : '指定されたURLのフィードが見つかりませんでした。',
    'not_exists_error' : 'フィードが登録されていない為、削除できません。',
    'already_exists_error' : '既に登録されているフィードです。',
    'url_required_error' : 'フィードのURLは必須です。',
    'parse_error' : 'フィードのパースに失敗しました。',
    'url_error' : 'フィードのURLが正しくありません。',
    'invalid_value_error' : '不正な値が入力されました。',
}