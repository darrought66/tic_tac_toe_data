import { DynamoDBClient, GetItemCommand } from "@aws-sdk/client-dynamodb";
import { unmarshall } from "@aws-sdk/util-dynamodb";

const client = new DynamoDBClient();
const TABLE_NAME = "game_states";

export const handler = async (event) => {
    // Parse game_state_id from the incoming event (e.g., query string or body)
    const gameStateId = event.game_state_id || (event.queryStringParameters && event.queryStringParameters.game_state_id);

    if (!gameStateId) {
        return {
            statusCode: 400,
            body: JSON.stringify({ error: "Missing game_state_id" }),
        };
    }

    const params = {
        TableName: TABLE_NAME,
        Key: {
            game_state_id: { S: gameStateId } // Assuming game_state_id is a String type
        }
    };

    try {
        const command = new GetItemCommand(params);
        const { Item } = await client.send(command);

        if (!Item) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: "Game state not found" }),
            };
        }

        // Convert raw DynamoDB attribute values to a clean JavaScript object
        return {
            statusCode: 200,
            body: JSON.stringify({ item: unmarshall(Item) }),
        };
    } catch (error) {
        console.error("Error reading DynamoDB:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: "Internal Server Error" }),
        };
    }
};
