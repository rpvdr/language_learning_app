/**
 * Generated by orval v7.9.0 🍺
 * Do not edit manually.
 * German Language Learning API
 * API for managing German words, phrases, components, examples, and semantic groups.
 * OpenAPI spec version: 1.0.0
 */
import {
  useMutation
} from '@tanstack/react-query';
import type {
  MutationFunction,
  UseMutationOptions,
  UseMutationResult
} from '@tanstack/react-query';

import * as axios from 'axios';
import type {
  AxiosError,
  AxiosRequestConfig,
  AxiosResponse
} from 'axios';

import type {
  HTTPValidationError,
  ProfileUpdate,
  UserResponse
} from '.././model';





/**
 * @summary Update Profile
 */
export const updateProfileApiMeProfilePut = (
    profileUpdate: ProfileUpdate, options?: AxiosRequestConfig
 ): Promise<AxiosResponse<UserResponse>> => {
    
    
    return axios.default.put(
      `/api/me/profile`,
      profileUpdate,options
    );
  }



export const getUpdateProfileApiMeProfilePutMutationOptions = <TError = AxiosError<HTTPValidationError>,
    TContext = unknown>(options?: { mutation?:UseMutationOptions<Awaited<ReturnType<typeof updateProfileApiMeProfilePut>>, TError,{data: ProfileUpdate}, TContext>, axios?: AxiosRequestConfig}
): UseMutationOptions<Awaited<ReturnType<typeof updateProfileApiMeProfilePut>>, TError,{data: ProfileUpdate}, TContext> => {

const mutationKey = ['updateProfileApiMeProfilePut'];
const {mutation: mutationOptions, axios: axiosOptions} = options ?
      options.mutation && 'mutationKey' in options.mutation && options.mutation.mutationKey ?
      options
      : {...options, mutation: {...options.mutation, mutationKey}}
      : {mutation: { mutationKey, }, axios: undefined};

      


      const mutationFn: MutationFunction<Awaited<ReturnType<typeof updateProfileApiMeProfilePut>>, {data: ProfileUpdate}> = (props) => {
          const {data} = props ?? {};

          return  updateProfileApiMeProfilePut(data,axiosOptions)
        }

        


  return  { mutationFn, ...mutationOptions }}

    export type UpdateProfileApiMeProfilePutMutationResult = NonNullable<Awaited<ReturnType<typeof updateProfileApiMeProfilePut>>>
    export type UpdateProfileApiMeProfilePutMutationBody = ProfileUpdate
    export type UpdateProfileApiMeProfilePutMutationError = AxiosError<HTTPValidationError>

    /**
 * @summary Update Profile
 */
export const useUpdateProfileApiMeProfilePut = <TError = AxiosError<HTTPValidationError>,
    TContext = unknown>(options?: { mutation?:UseMutationOptions<Awaited<ReturnType<typeof updateProfileApiMeProfilePut>>, TError,{data: ProfileUpdate}, TContext>, axios?: AxiosRequestConfig}
 ): UseMutationResult<
        Awaited<ReturnType<typeof updateProfileApiMeProfilePut>>,
        TError,
        {data: ProfileUpdate},
        TContext
      > => {

      const mutationOptions = getUpdateProfileApiMeProfilePutMutationOptions(options);

      return useMutation(mutationOptions );
    }
    