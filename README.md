# GraphForce

🧠 **GraphQL Suggestion Brute Forcer**  
📌 **Coded by Tal3at**

GraphForce is a brute-force tool to discover hidden GraphQL mutations/queries via error-based "Did you mean" suggestions.

## Steps to Use

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/itsTal3at/GraphForce.git
   ```

2. **Navigate to the Project Directory:**
   ```bash
   cd GraphForce
   ```

3. **Place Dollar Signs Around the Mutation Name:**
   When specifying the mutation name in your request, make sure to surround it with dollar signs (`$`). For example, if the mutation is `createUser`, write it as `$createUser$`.

4. **Run the Tool:**
   ```bash
   python3 GraphForce.py -r request.txt -w mutationFieldWordlist.txt
   ```








