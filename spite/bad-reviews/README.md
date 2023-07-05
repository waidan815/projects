
# architecture

Get reviews from here: https://letterboxd.com/djrennie7/films/reviews/

calls are unfortunately not persistent. 
need to decide whether:
    to constantly look for new reviews


program logic:
    connect to postgresdb
    check if there are reviews there and what latest review was 

    pull data from film site with constraints i.e. don't look for data we already have
    push that to open ai
    get results back in useable format


    


or 

program logic:
    get reviews from site
    transform, send to openai
    get results back in useable format
    push to postgres
        delete duplicates

    or only push select data to postgres



    # bottlenecks
    - openai spending
    - speed



    # useful stuff

    sees how many tokens a text is - https://platform.openai.com/tokenizer 

    some examples  - https://github.com/openai/openai-cookbook/blob/main/examples/How_to_format_inputs_to_ChatGPT_models.ipynb

    playground - https://platform.openai.com/playground?mode=complete

    more examples - https://platform.openai.com/examples

    billing/useage stuff - https://platform.openai.com/account/billing/overview 