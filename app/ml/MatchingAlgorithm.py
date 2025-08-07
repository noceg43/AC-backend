import numpy as np
from sklearn.decomposition import PCA
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment
import json

class AlphaConnectMatcher:
    def __init__(self, user_answers: dict):
        """
        Initialize the matcher

        Args:
            user_answers (dict): ...
        """
        self.answers = user_answers
        self.weight_matrix = self.__generate_weight_matrix()
        self.user_dataframe = self.__generate_user_dataframe()
        self.users = list(self.user_dataframe.keys())
        self.users_array = np.array(list(self.user_dataframe.values()))



    def create_matching(self):
        pca = PCA(n_components=3)
        user_space_reduced = pca.fit_transform(self.users_array)
        dist_matrix = cdist(user_space_reduced, user_space_reduced)

        np.fill_diagonal(dist_matrix, np.inf)

        n = len(user_space_reduced)
        assert n % 2 == 0, "Serve un numero pari di punti per coppie perfette."

        left_indices = np.arange(0, n, 2)
        right_indices = np.arange(1, n, 2)

        cost_matrix = dist_matrix[np.ix_(left_indices, right_indices)]

        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        # Costruisci le coppie finali (indici originali)
        pairs = [(left_indices[i], right_indices[j]) for i, j in zip(row_ind, col_ind)]

        pairs = [(self.users[el[0]], self.users[el[1]], round(self.__get_disparity_value(self.users[el[0]], self.users[el[1]]), 3)) for el in pairs]

        pairs = sorted(pairs, key=lambda x: x[2])
        return pairs
        
    def __generate_weight_matrix(self):
        answer_wheights = {}
        checked_answer = set()
        raw_data = self.answers["data"]
        for question_user in raw_data:
            question_id = question_user["question"]["id"]
            answers = question_user["question"]["answers"]
            for answer in answers:
                id = answer["id"]
                weight = answer["weight"]
                if question_id not in answer_wheights.keys():
                    answer_wheights[question_id] = {}
                    answer_wheights[question_id][id] = weight
                    checked_answer.add(id)
                elif id not in checked_answer:
                    answer_wheights[question_id][id] =  weight
                    checked_answer.add(id)
                else:
                    pass
        # Order keys
        answer_wheights = dict(sorted(answer_wheights.items()))

        answer_wheights = {
            k: v
            for subdict in answer_wheights.values()
            for k, v in subdict.items()
        }

        return answer_wheights

    def __generate_user_dataframe(self):
        raw_data = self.answers["data"]
        user_answers = {}
        for member_answer in raw_data:
            all_answer = member_answer["member_answers"]
            for answer in all_answer:
                question_id = answer["question"]["id"]
                user_id = answer["member"]["id"]
                answer_id = answer["answer"]["id"]

                if user_id not in user_answers.keys():
                    user_answers[user_id] = {}
                user_answers[user_id][question_id] = self.weight_matrix[answer_id]
        sorted_user_answers = {
            outer_k: dict(sorted(inner_dict.items()))
            for outer_k, inner_dict in user_answers.items()
        }

        for k,v in sorted_user_answers.items():
            answer_dict = sorted_user_answers[k]

            sorted_user_answers[k] = [v for v in answer_dict.values()]

        return sorted_user_answers
    
    def __error_function(self, ans_1, ans_2):
        error = 0
        for i in range(len(ans_1)):
            error += abs(ans_1[i] - ans_2[i])
        return error

    
    def __get_disparity_value(self, user_id, user_id_2):
        ans_1 = list(self.user_dataframe[user_id])
        ans_2 = list(self.user_dataframe[user_id_2])
        return self.__error_function(ans_1, ans_2)



