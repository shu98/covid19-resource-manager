def search_keywords(query_keywords, all_resources):
    # List of words that are too common, leading to false positives
    common_words = set((
        'the', 'and', 'a', 'of', 'to', 'at', 'be', 'this', 'in', 'is', 'it',
        'for', 'as'
    ))

    # Keyword Search
    final_resources = []
    if len(query_keywords) > 0 and len(query_keywords[0]) > 0:
        for record in all_resources:

            # Process the iped_ad field
            if record['iped_ad'] == 'Both':
                iped_ad = 'Inpatient/ED Ambulatory/Discharge'
            elif record['iped_ad'] == None:
                iped_ad = ''
            else:
                iped_ad = record['iped_ad']

            for keyword in query_keywords:
                if keyword in common_words:
                    continue

                # If big enough, search directly on text
                if len(keyword) > 3:
                    cond = keyword.lower() in record['title'].lower() \
                        or keyword.lower() in record['description'].lower() \
                        or keyword.lower() in record['institution'].lower() \
                        or keyword.lower() in record['link'].lower() \
                        or keyword.lower() in record['resource_type'].lower() \
                        or keyword.lower() in iped_ad.lower() \
                        or keyword.lower() in ' '.join(record['categories']).lower()
                # If it's too small, break it up by spaces and look for exact word matches. Reduces noise.
                else:
                    cond = keyword.lower() in record['title'].lower().split(' ') \
                        or keyword.lower() in record['description'].lower().split(' ') \
                        or keyword.lower() in record['institution'].lower() \
                        or keyword.lower() in record['link'].lower() \
                        or keyword.lower() in record['resource_type'].lower() \
                        or keyword.lower() in iped_ad.lower() \
                        or keyword.lower() in ' '.join(record['categories']).lower().split(' ')
                if cond:
                    final_resources.append(record)
    return final_resources
