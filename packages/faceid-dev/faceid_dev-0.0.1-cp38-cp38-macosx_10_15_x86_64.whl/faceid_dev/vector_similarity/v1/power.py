def update_person_embedding(fa_emb_str, face):
    emb = "cube(ARRAY" + fa_emb_str+ ")"
    update_query = "UPDATE faces SET embedding = " + emb + " WHERE name = '" + str(face.name) + "';"
    return update_query

def compute_similarity_by_embedding(embedding, gender, similarity_threshold, limit):
    emb = "cube(ARRAY" + embedding + ")"
    query = (
        "SELECT sub.* "
        "FROM "
        "( "
            "SELECT *, (1-(POWER(( embedding <-> " + emb + " ),2)/2))*100 AS similarity "
            "FROM faces "
        ") AS sub "
        "WHERE sub.gender = '" + gender + "' AND sub.similarity > "+similarity_threshold+" "
        "ORDER BY sub.similarity DESC "
        "LIMIT " + str(limit) + ";"
        )
    return query

def compute_similarity(fa_emb_str, inp_face, similarity_threshold, limit):
    emb = "cube(ARRAY" + fa_emb_str + ")"
    query = (
        "SELECT sub.* "
        "FROM "
        "( "
            "SELECT *, (1-(POWER(( embedding <-> " + emb + " ),2)/2))*100 AS similarity "
            "FROM faces "
        ") AS sub "
        "WHERE sub.gender = '" + inp_face.gender + "' AND sub.similarity > "+similarity_threshold+""
        "ORDER BY sub.similarity DESC "
        "LIMIT " + str(limit) + ";"
        )
    return query