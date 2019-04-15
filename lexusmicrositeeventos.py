def eventOSSet(conditions, current_answers, previous_answers, consumer_id, flow_id, question_id, question_keyword):
    import requests
    import json

    delete_microsite_consumer_survey_update(consumer_id, flow_id)

    login = {
        'username': '12673lexuseos',
        'password': '_&MnB4a3r3UaEqP-'
    }

     keyword_mapping = {
    "first_name": null,
    "last_name": null,
    "email": null,
    "zip": null,
    "street": null,
    "apt": null,
    "city": null,
    "state": null,
    "phone": null,
    "efn_edid": null,
    }

    url = 'https://api.eshots.com'
    token = None

    # Login and get user token
    headers = {'Content-Type': 'application/json'}

    # Post request to retrieve auth token
    r = requests.post(url+'/authtoken', data=json.dumps(login), headers=headers)

    if r.status_code == requests.codes.ok:
        response = json.loads(r.text)

        if 'token' in response:
            token = response['token']
        else:
            print 'token not in repsonse'

        # if we have the auth token, format and upload the consumer data
        if token:

            consumer_answers = {"answers" : {}}
            epass = None
            location = None

            # loop through each potential question and grab consumers answer(s)
            for mapping_key, mapping_value in keyword_mapping.iteritems():

                # loop through all previous consumer answers and check for match
                for previous_answer_key in previous_answers:
                    survey_item = CommandItem(previous_answer_key, previous_answers[previous_answer_key])
                    if survey_item.get_keywords() == mapping_key:
                        # create list of answers
                        ans_value = survey_item.get_value().split(',')
                        # remove duplicate answers
                        ans_value = list(set(ans_value))

                        # choice question
                        if mapping_value:
                            tmp_lst = []
                            # loop through all chosen consumer answers
                            for answer in ans_value:
                                # all possible mapped answers
                                for map_value in mapping_value:
                                    if answer == map_value:
                                        if answer == '' or answer.lower() == 'no response':
                                            tmp_lst.append('na')
                                        else:
                                            tmp_lst.append(str(keyword_mapping[mapping_key][answer]))

                            # append mapped consumer answers(s)
                            if tmp_lst:
                                consumer_answers['answers'][mapping_key] = tmp_lst

                        # text question
                        else:
                            if str(ans_value[0]) != '' and str(ans_value[0]).lower() != 'no response' and str(ans_value[0]).lower() != 'none':
                                # append text question answer to consumer object
                                consumer_answers['answers'][mapping_key] = str(ans_value[0])

                    elif survey_item.get_keywords() == 'epass':
                        epass = survey_item.get_value()

                # loop through all current consumer answers and check for match
                for current_answer_key in current_answers:
                    survey_item = CommandItem(current_answer_key, current_answers[current_answer_key])
                    if survey_item.get_keywords() == mapping_key:
                        # create list of answers
                        ans_value = survey_item.get_value().split(',')
                        # remove duplicate answers
                        ans_value = list(set(ans_value))

                        # choice question
                        if mapping_value:
                            tmp_lst = []
                            # loop through all chosen consumer answers
                            for answer in ans_value:
                                # all possible mapped answers
                                for map_value in mapping_value:
                                    if answer == map_value:
                                        if answer == '' or answer.lower() == 'no response':
                                            tmp_lst.append('na')
                                        else:
                                            tmp_lst.append(str(keyword_mapping[mapping_key][answer]))

                            # append mapped consumer answers(s)
                            if tmp_lst:
                                consumer_answers['answers'][mapping_key] = tmp_lst

                        # text question
                        else:
                            if str(ans_value[0]) != '' and str(ans_value[0]).lower() != 'no response' and str(ans_value[0]).lower() != 'none':
                                # append text question answer to consumer object
                                consumer_answers['answers'][mapping_key] = str(ans_value[0])

                    elif survey_item.get_keywords() == 'epass':
                        epass = survey_item.get_value()

            cursor = connection.cursor()

            # get consumers epass
            if epass:
                consumer_answers['epass'] = str(epass)

            # get consumers location
            qry = """
                SELECT DISTINCT E.name, F.event_day_ID, F.client_license_ID
                FROM Events E
                STRAIGHT_JOIN Event_Days ED ON ED.event_ID = E.event_ID
                STRAIGHT_JOIN Footprints F ON F.event_day_ID = ED.event_day_ID
                WHERE TRUE
                AND F.consumer_ID = %s
                ORDER BY F.create_DTM DESC;
            """

            cursor.execute(qry, [consumer_id])
            if cursor.rowcount:
                result = cursor.fetchone()
                location = str(result[0])
                event_day_id = str(result[1])
                client_license_id = str(result[2])

            if location:
                consumer_answers['location'] = location

            if event_day_id:
                consumer_answers['answers']['last_event_day'] = event_day_id

            if client_license_id:
                consumer_answers['answers']['campaign'] = client_license_id

            # get upload time
            cursor.execute("SELECT DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%S');")
            time = str(cursor.fetchone()[0])

            if time:
                consumer_answers['datetime'] = time

            headers = {
                'Authorization': 'Bearer ' + str(token),
                'Content-Type': 'application/json'
            }

            # get consumers event token
            qry = """
                SELECT DISTINCT F.event_token_ID
                FROM Footprints F
                WHERE TRUE
                AND F.consumer_ID = %s
                ORDER BY F.create_DTM DESC;
             """

            cursor.execute(qry, [consumer_id])
            if cursor.rowcount:
                consumer_answers['epass'] = str(cursor.fetchone()[0])

            # Send consumer data to EOS via post request
            r = requests.post(url+'/interaction', data=json.dumps(consumer_answers), headers=headers)

            # Consumer was successfully created in EOS
            # if r.status_code == 201:
            #     response = json.loads(r.text)
            #     print response
            # else:
            #     print "ERROR"
            #     print r.status_code

    # else:
    #     print "ERROR"
    #     print r.status_code


def eventOSGet(conditions, current_answers, previous_answers, consumer_id, flow_id, question_id, question_keyword):
    import requests
    import json

    delete_microsite_consumer_survey_update(consumer_id, flow_id, question_id, question_keyword)

    login = {
        'username': '12673lexuseos',
        'password': '_&MnB4a3r3UaEqP-'
    }

     keyword_mapping = {
    "first_name": null,
    "last_name": null,
    "email": null,
    "zip": null,
    "street": null,
    "apt": null,
    "city": null,
    "state": null,
    "phone": null,
    "efn_edid": null,
    }

    url = 'https://api.eshots.com'
    token = None

    # Login and get user token
    headers = {'Content-Type': 'application/json'}

    # Post request to retrieve auth token
    r = requests.post(url+'/authtoken', data=json.dumps(login), headers=headers)

    if r.status_code == requests.codes.ok:
        response = json.loads(r.text)

        if 'token' in response:
            token = response['token']
        else:
            print 'token not in repsonse'

        # if we have the auth token, format and upload the consumer data
        if token:

            consumer_answers = {"answers" : {}}
            epass = None
            location = None

            # loop through each potential question and grab consumers answer(s)
            for mapping_key, mapping_value in keyword_mapping.iteritems():

                # loop through all previous consumer answers and check for match
                for previous_answer_key in previous_answers:
                    survey_item = CommandItem(previous_answer_key, previous_answers[previous_answer_key])
                    if survey_item.get_keywords() == mapping_key:
                        # create list of answers
                        ans_value = survey_item.get_value().split(',')
                        # remove duplicate answers
                        ans_value = list(set(ans_value))

                        # choice question
                        if mapping_value:
                            tmp_lst = []
                            # loop through all chosen consumer answers
                            for answer in ans_value:
                                # all possible mapped answers
                                for map_value in mapping_value:
                                    if answer == map_value:
                                        if answer == '' or answer.lower() == 'no response':
                                            tmp_lst.append('na')
                                        else:
                                            tmp_lst.append(str(keyword_mapping[mapping_key][answer]))

                            # append mapped consumer answers(s)
                            if tmp_lst:
                                consumer_answers['answers'][mapping_key] = tmp_lst

                        # text question
                        else:
                            if str(ans_value[0]) != '' and str(ans_value[0]).lower() != 'no response' and str(ans_value[0]).lower() != 'none':
                                # append text question answer to consumer object
                                consumer_answers['answers'][mapping_key] = str(ans_value[0])

                    elif survey_item.get_keywords() == 'epass':
                        epass = survey_item.get_value()

                # loop through all current consumer answers and check for match
                for current_answer_key in current_answers:
                    survey_item = CommandItem(current_answer_key, current_answers[current_answer_key])
                    if survey_item.get_keywords() == mapping_key:
                        # create list of answers
                        ans_value = survey_item.get_value().split(',')
                        # remove duplicate answers
                        ans_value = list(set(ans_value))

                        # choice question
                        if mapping_value:
                            tmp_lst = []
                            # loop through all chosen consumer answers
                            for answer in ans_value:
                                # all possible mapped answers
                                for map_value in mapping_value:
                                    if answer == map_value:
                                        if answer == '' or answer.lower() == 'no response':
                                            tmp_lst.append('na')
                                        else:
                                            tmp_lst.append(str(keyword_mapping[mapping_key][answer]))

                            # append mapped consumer answers(s)
                            if tmp_lst:
                                consumer_answers['answers'][mapping_key] = tmp_lst

                        # text question
                        else:
                            if str(ans_value[0]) != '' and str(ans_value[0]).lower() != 'no response' and str(ans_value[0]).lower() != 'none':
                                # append text question answer to consumer object
                                consumer_answers['answers'][mapping_key] = str(ans_value[0])

                    elif survey_item.get_keywords() == 'epass':
                        epass = survey_item.get_value()

            cursor = connection.cursor()

            # get consumers epass
            if epass:
                consumer_answers['epass'] = str(epass)

            # get consumers location
            qry = """
                SELECT DISTINCT E.name
                FROM Events E
                STRAIGHT_JOIN Event_Days ED ON ED.event_ID = E.event_ID
                STRAIGHT_JOIN Footprints F ON F.event_day_ID = ED.event_day_ID
                WHERE TRUE
                AND F.consumer_ID = %s
                ORDER BY F.create_DTM DESC;
            """

            cursor.execute(qry, [consumer_id])
            if cursor.rowcount:
                location = str(cursor.fetchone()[0])

            if location:
                consumer_answers['location'] = str(location)

            # get upload time
            cursor.execute("SELECT DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%S');")
            time = str(cursor.fetchone()[0])

            if time:
                consumer_answers['datetime'] = time

            headers = {
                'Authorization': 'Bearer ' + str(token),
                'Content-Type': 'application/json'
            }

            # Send consumer data to EOS via post request
            r = requests.post(url+'/consumer', data=json.dumps(consumer_answers), headers=headers)

        # Consumer was successfully created in EOS
        if r.status_code == 200:
            eos_consumer_response = json.loads(r.text)
            insert_microsite_consumer_survey_update(consumer_id=consumer_id, flow_id=flow_id, question_id=question_id,
                                                    question_keyword=question_keyword, display_flag=None,
                                                    survey_action_id=None, required_flag=None,
                                                    short_text=None, long_text=None, placeholder_text=None,
                                                    answers=None, cache=str(eos_consumer_response))
            return "1"
        else:
            return "0"

    else:
        return "0"


def eventOSMap(conditions, current_answers, previous_answers, consumer_id, flow_id, question_id, question_keyword):
    returnValue = None
    answers = []

    choice_mapping = {
         "certificate": {
        "36099": "y",
        "45276": "n",
    },
    "dealer_contact": {
        "194": "y",
        "195": "n",
    },
    }  

    cursor = connection.cursor()
    cursor.execute("SELECT DE.data_element_type_ID " +
                   "FROM   Questions Q " +
                   "JOIN   R_Question_Data_Element RQDE ON Q.question_ID = RQDE.question_ID " +
                   "JOIN   Data_Elements DE ON RQDE.data_element_ID = DE.data_element_ID " +
                   "WHERE  Q.question_id = %s", [question_id])
    result = cursor.fetchone()
    data_element_type_id = result[0]

    cursor.execute("SELECT cache " +
                   "FROM   Microsite_Consumer_Survey_Updates " +
                   "WHERE  consumer_id = %s", [consumer_id])
    data = cursor.fetchone()

    if data:
        eos_answer_cache = eval(data[0])
        answers = eos_answer_cache['answers']

    if question_keyword in answers:
        returnValue = answers[question_keyword]

        if data_element_type_id == 1:
            if question_keyword in choice_mapping:
                response_value = str(answers[question_keyword][0])
                if response_value in choice_mapping[question_keyword]:
                    returnValue = int(choice_mapping[question_keyword][response_value])

    return returnValue


def eventOSVerify(conditions, current_answers, previous_answers, consumer_id, flow_id, question_id, question_keyword):
    returnValue = "0"

    cursor = connection.cursor()
    cursor.execute("SELECT cache " +
                   "FROM   Microsite_Consumer_Survey_Updates " +
                   "WHERE  consumer_id = %s", [consumer_id])
    data = cursor.fetchone()
    if data:
        eos_answer_cache = eval(data[0])
        answers = eos_answer_cache['answers']

        verified_question_answer = None

    else:
        return returnValue
    for current_answer_key in current_answers:
        survey_item = CommandItem(current_answer_key, current_answers[current_answer_key])
        if survey_item.get_keywords() == 'phone':
            verified_question_answer = survey_item.get_value()

    if 'phone' in answers and verified_question_answer:
        if str(answers['phone']) == str(verified_question_answer):
            return "1"

    return returnValue
