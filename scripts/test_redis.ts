import Redis from 'ioredis';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.join(__dirname, '../.env') });

async function testRedis() {
    console.log('Testing Redis connection...');
    console.log('Host:', process.env.REDIS_HOST);
    console.log('Port:', process.env.REDIS_PORT);

    const redis = new Redis({
        host: process.env.REDIS_HOST,
        port: parseInt(process.env.REDIS_PORT || '6379'),
        username: 'default',
        password: process.env.REDIS_PASSWORD,
        connectTimeout: 10000,
        retryStrategy: (times) => {
            if (times > 3) return null;
            return 2000;
        }
    });

    try {
        await redis.ping();
        console.log('Redis connected successfully! (PONG)');

        await redis.set('test-key', 'hello');
        const val = await redis.get('test-key');
        console.log('Redis set/get work:', val);

    } catch (err: any) {
        console.error('Redis connection failed:', err.message);
    } finally {
        redis.disconnect();
    }
}

testRedis();
